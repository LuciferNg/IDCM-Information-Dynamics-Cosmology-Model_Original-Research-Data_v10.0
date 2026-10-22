#!/usr/bin/env python3
"""
O70 — 29: Iterative Extreme Ray Completion
============================================
Iterative: 用 fail points 嘅 active-set null space 不斷補齊 extreme rays,
直到 N 次 random test 全部 PASS (K ⊆ cone(rays)).

收斂準則: 連續 2 rounds 0 fail (500 random each)。
"""
import os, sys, numpy as np
from scipy.optimize import linprog
from scipy.linalg import null_space, qr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R0 = np.load(os.path.join(DATA, "15_all_rays.npy"))
print(f"Mori: {M.shape}, 初始 rays: {R0.shape}")

def boundary_point(d):
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    return res.x if res.success else None

def in_cone(v, gens):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success

# ray set (normalized, sign-convention)
rays = {}
def add(r0):
    nrm = np.linalg.norm(r0)
    if nrm < 1e-12:
        return
    r = r0 / nrm
    for x in r:
        if abs(x) > 1e-10:
            if x < 0:
                r = -r
            break
    rays[tuple(np.round(r, 6))] = r

for r in R0:
    add(r)

rng = np.random.default_rng(42)
round_no = 0
while True:
    round_no += 1
    # random test
    fails = []
    for i in range(500):
        d = rng.standard_normal(32)
        t = boundary_point(d)
        if t is None:
            continue
        if not in_cone(t, np.array(list(rays.values()))):
            fails.append((t, d))
    print(f"\nRound {round_no}: {len(rays)} rays, {len(fails)}/500 FAIL")
    
    if len(fails) == 0:
        print(f"✅ 收斂! {len(rays)} extreme rays complete (500 random tests PASS)")
        break
    
    # 由 fail points 提取新 rays
    n_new = 0
    for t, d in fails:
        v = M @ t
        active = np.where(np.abs(v) < 1e-6)[0]
        # 試 rank-revealing 揀 31 條 (用幾種 pivot 策略)
        candidates = []
        A_rows = M[active]
        # QR pivoting
        Qq, Rr, piv = qr(A_rows.T, pivoting=True)
        if len(piv) >= 31:
            best31 = active[piv[:31]]
            M31 = M[best31]
            if np.linalg.matrix_rank(M31) == 31:
                ns = null_space(M31)
                if ns.shape[1] == 1:
                    candidates.append(ns[:, 0])
        # 隨機 31-subset 補充
        for _ in range(30):
            if len(active) < 31:
                break
            idx = rng.choice(active, 31, replace=False)
            Mi = M[idx]
            if np.linalg.matrix_rank(Mi) < 31:
                continue
            ns = null_space(Mi)
            if ns.shape[1] == 1:
                candidates.append(ns[:, 0])
        for r in candidates:
            if (M @ r).min() < -1e-8:
                r = -r
                if (M @ r).min() < -1e-8:
                    continue
            before = len(rays)
            add(r)
            if len(rays) > before:
                n_new += 1
    print(f"  round {round_no} 新增 {n_new} rays → 總數 {len(rays)}")
    if n_new == 0:
        print("⚠️ 冇新 rays — 卡住, 可能 fail 係數值假象 or 需要其他策略")
        break

R_final = np.array(list(rays.values()))
np.save(os.path.join(DATA, "29_complete_extreme_rays.npy"), R_final)
print(f"\nSaved → data/29_complete_extreme_rays.npy ({R_final.shape})")
print(f"總 extreme rays: {len(R_final)}")
