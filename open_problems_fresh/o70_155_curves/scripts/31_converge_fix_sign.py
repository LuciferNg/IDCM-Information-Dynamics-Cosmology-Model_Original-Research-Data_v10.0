#!/usr/bin/env python3
"""
O70 — 31: 收斂 + sign 修正檢查
================================
1. Sign-convention 修正後: 203 入面有幾多條 = 舊 99?
2. 補埋最後 1 個 fail (如果有真漏)
3. 1000+ random 再驗證
"""
import os, sys, numpy as np
from scipy.optimize import linprog
from scipy.linalg import null_space, qr

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

M = np.load(os.path.join(DATA, "22_mori_cone_rays_32d.npy")).astype(float)
R = np.load(os.path.join(DATA, "29_complete_extreme_rays.npy"))
R99 = np.load(os.path.join(DATA, "15_all_rays.npy"))

def signfix(r):
    for x in r:
        if abs(x) > 1e-10:
            return r if x > 0 else -r
    return r

# sign-fix 全部 rays
Rf = np.array([signfix(r) for r in R])
R99f = np.array([signfix(r) for r in R99])

# 對比
print("─── sign-fix 後對比 ───")
diffs = []
for i, r in enumerate(Rf):
    # 搵 R99 入面相同方向 (±)
    dots = R99f @ r
    if np.max(np.abs(dots)) < 1 - 1e-8:
        diffs.append(i)
print(f"203 rays 入面唔喺 99: {len(diffs)}")
print(f"→ 新增 {len(diffs)} 條, 舊 99 全部保留: {len(Rf) - len(diffs) == 99}")

# in_cone
def in_cone(v, gens):
    n = gens.shape[0]
    res = linprog(np.zeros(n), A_eq=gens.T, b_eq=v, bounds=[(0, None)] * n, method='highs')
    return res.success

def boundary_point(d):
    res = linprog(d, A_ub=-M, b_ub=np.zeros(len(M)), bounds=[(-1, 1)] * 32, method='highs')
    return res.x if res.success else None

# 補漏 loop
rng = np.random.default_rng(2026)
rays_dict = {tuple(np.round(r, 6)): r for r in Rf}
print(f"\n─── 補漏 iterations ───")
for it in range(8):
    vals = np.array(list(rays_dict.values()))
    fails = []
    for i in range(800):
        d = rng.standard_normal(32)
        t = boundary_point(d)
        if t is None:
            continue
        if not in_cone(t, vals):
            fails.append(t)
    print(f"  iter {it}: {len(vals)} rays, {len(fails)}/800 fail")
    if not fails:
        print("  ✅ 收斂!")
        break
    n_new = 0
    for t in fails:
        v = M @ t
        active = np.where(np.abs(v) < 1e-6)[0]
        cands = []
        # QR pivoting
        Qq, Rr_, piv = qr(M[active].T, pivoting=True)
        if len(piv) >= 31:
            best31 = active[piv[:31]]
            if np.linalg.matrix_rank(M[best31]) == 31:
                ns = null_space(M[best31])
                if ns.shape[1] == 1:
                    cands.append(ns[:, 0])
        for _ in range(20):
            if len(active) < 31:
                break
            idx = rng.choice(active, 31, replace=False)
            Mi = M[idx]
            if np.linalg.matrix_rank(Mi) < 31:
                continue
            ns = null_space(Mi)
            if ns.shape[1] == 1:
                cands.append(ns[:, 0])
        for r in cands:
            if (M @ r).min() < -1e-8:
                r = -r
                if (M @ r).min() < -1e-8:
                    continue
            rn = signfix(r / np.linalg.norm(r))
            key = tuple(np.round(rn, 6))
            if key not in rays_dict:
                rays_dict[key] = rn
                n_new += 1
    print(f"  新增 {n_new} → {len(rays_dict)}")

Rf2 = np.array(list(rays_dict.values()))
np.save(os.path.join(DATA, "31_complete_extreme_rays_v2.npy"), Rf2)
print(f"\nFinal: {len(Rf2)} extreme rays saved → data/31_complete_extreme_rays_v2.npy")

# Final: 5000 random test
print(f"\n─── Final 5000 random test ───")
fails = 0
for i in range(5000):
    d = rng.standard_normal(32)
    t = boundary_point(d)
    if t is None:
        continue
    if not in_cone(t, Rf2):
        fails += 1
print(f"{fails}/5000 FAIL → {'✅ COMPLETE' if fails == 0 else '⚠️ 仲有漏'}")
