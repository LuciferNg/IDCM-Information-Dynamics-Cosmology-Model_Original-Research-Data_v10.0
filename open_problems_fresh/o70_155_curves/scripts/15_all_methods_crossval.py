#!/usr/bin/env python3
"""
O70 — 15: Kähler Cone Extreme Rays — 全面交叉驗證
===================================================
方法 A: LP 標準形 (min c·t s.t. Q·t ≥ 0, -1 ≤ t_j ≤ 1)
方法 B: 方向隨機 + 活動集過完備
方法 C: 二次規劃 (min ||Q·t||^2 s.t. ||t||=1)
方法 D: 隨機子集檢驗 (隨機揀 32 條 constraints 解 system)
方法 E: 對偶錐頂點 (find extreme rays of dual cone)
方法 F: 迭代投影 (逐次投影到 active constraints)
"""

import sys, os, math, json, numpy as np
from scipy.optimize import minimize, linprog
import scipy.linalg
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 15: 全面交叉驗證")
print("=" * 72)

# Load data
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])

# Compute Q_ij
t_test = phi ** (-np.arange(36))
t32 = np.array([t_test[b-1] for b in basis])
eps = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    tp = t32.copy(); tm = t32.copy()
    tp[j] += eps; tm[j] -= eps
    cvp = np.array(cy.compute_curve_volumes(tp))
    cvm = np.array(cy.compute_curve_volumes(tm))
    Q[:, j] = (cvp - cvm) / (2*eps)

Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)
print(f"Q: 185×32, rank: {np.linalg.matrix_rank(Qn)}")

all_rays = {}  # name -> list of rays

# ===== Method A: LP Standard Form =====
print("\n" + "=" * 60)
print("方法 A: LP Standard Form (Σt=1)")
print("=" * 60)
# min c·t s.t. Q·t ≥ 0, Σt = 1
# Normalization prevents t = 0

rays_A = []
rays_A_set = set()
n_trials = 500
for trial in range(n_trials):
    c = np.random.randn(32)
    c = c / np.linalg.norm(c)
    
    res = linprog(c, A_ub=-Qn, b_ub=np.zeros(185),
                  A_eq=np.ones((1, 32)), b_eq=np.array([1.0]),
                  method='highs')
    
    if not res.success:
        continue
    
    t = res.x
    norm_t = np.linalg.norm(t)
    if norm_t < 1e-15:
        continue
    t = t / norm_t
    vols = Qn @ t
    n_active = np.sum(np.abs(vols) < 1e-6)
    
    key = tuple(np.round(t, decimals=6))
    if key not in rays_A_set:
        rays_A_set.add(key)
        rays_A.append(t)
        if len(rays_A) <= 10:
            print(f"  Ray {len(rays_A)}: active={n_active}")

print(f"  Method A: {len(rays_A)} unique rays")
if len(rays_A) > 0:
    R = np.array(rays_A)
    print(f"  Rank: {np.linalg.matrix_rank(R)}/{len(rays_A)}")
    all_rays['A'] = R

# ===== Method B: Active Set Refinement =====
print("\n" + "=" * 60)
print("方法 B: Active Set Refinement (二次優化)")
print("=" * 60)
# 1. LP 找到 boundary point
# 2. Active constraints → 解 min ||Q_active @ t||² s.t. ||t||=1
# 3. 檢查結果

rays_B = []
rays_B_set = set()
n_trials = 500

for trial in range(n_trials):
    c = np.random.randn(32)
    c = c / np.linalg.norm(c)
    
    # LP to find boundary
    res = linprog(c, A_ub=-Qn, b_ub=np.zeros(185),
                  A_eq=np.ones((1, 32)), b_eq=np.array([1.0]),
                  method='highs')
    if not res.success:
        continue
    
    t0 = res.x
    vols = Qn @ t0
    active = np.where(np.abs(vols) < 1e-6)[0]
    
    if len(active) < 32:
        continue
    
    # Refine: minimize ||Q_active @ t||² s.t. ||t||=1
    Q_active = Qn[active]
    
    # This is a quadratic problem: min t^T Q_active^T Q_active t s.t. t^T t = 1
    # Solution = eigenvector of Q_active^T Q_active with smallest eigenvalue
    H = Q_active.T @ Q_active
    eigvals, eigvecs = np.linalg.eigh(H)
    t_ray = eigvecs[:, 0]  # smallest eigenvalue = closest to null
    
    # Check sign
    if np.any(Qn @ t_ray < -1e-6):
        t_ray = -t_ray
    if not np.all(Qn @ t_ray > -1e-6):
        continue
    
    n_active_final = np.sum(np.abs(Qn @ t_ray) < 1e-6)
    
    key = tuple(np.round(t_ray, decimals=6))
    if key not in rays_B_set:
        rays_B_set.add(key)
        rays_B.append(t_ray)
        if len(rays_B) <= 10:
            print(f"  Ray {len(rays_B)}: active={n_active_final}")

print(f"  Method B: {len(rays_B)} unique rays")
if len(rays_B) > 0:
    R = np.array(rays_B)
    print(f"  Rank: {np.linalg.matrix_rank(R)}/{len(rays_B)}")
    all_rays['B'] = R

# ===== Method C: Quadratic Programming =====
print("\n" + "=" * 60)
print("方法 C: Quadratic Programming (sphere minimization)")
print("=" * 60)
# min ||Qn @ t||² s.t. ||t|| = 1, with directional bias
# = minimize ||Qn @ t||² + λ·(c·t)²

rays_C = []
rays_C_set = set()
n_trials = 500

for trial in range(n_trials):
    c = np.random.randn(32)
    c = c / np.linalg.norm(c)
    
    # Objective = ||Qn @ t||² + λ·(c·t)²
    # With λ large, this finds the boundary in direction c
    # With λ = 0, this finds the most null-like direction
    λ = 10.0
    H = Qn.T @ Qn + λ * np.outer(c, c)
    
    # Minimize t^T H t s.t. t^T t = 1
    # Solution = eigenvector with smallest eigenvalue
    eigvals, eigvecs = np.linalg.eigh(H)
    t = eigvecs[:, 0]
    
    # Check sign
    if np.any(Qn @ t < -1e-6):
        t = -t
    if not np.all(Qn @ t > -1e-6):
        # Try different λ
        for λ in [1.0, 0.1, 0.01]:
            H = Qn.T @ Qn + λ * np.outer(c, c)
            eigvals, eigvecs = np.linalg.eigh(H)
            t = eigvecs[:, 0]
            if np.any(Qn @ t < -1e-6):
                t = -t
            if np.all(Qn @ t > -1e-6):
                break
        else:
            continue
    
    n_active = np.sum(np.abs(Qn @ t) < 1e-6)
    
    key = tuple(np.round(t, decimals=6))
    if key not in rays_C_set:
        rays_C_set.add(key)
        rays_C.append(t)
        if len(rays_C) <= 10:
            print(f"  Ray {len(rays_C)}: active={n_active}")

print(f"  Method C: {len(rays_C)} unique rays")
if len(rays_C) > 0:
    R = np.array(rays_C)
    print(f"  Rank: {np.linalg.matrix_rank(R)}/{len(rays_C)}")
    all_rays['C'] = R

# ===== Method D: Random Subset =====
print("\n" + "=" * 60)
print("方法 D: Random Subset (32條 constraints 直接解)")
print("=" * 60)
# 隨機揀 32 條 rows from Qn
# 解 null space
# 檢查係咪喺 cone 入面

rays_D = []
rays_D_set = set()
n_trials = 50000

for trial in range(n_trials):
    # Pick 32 random rows
    idx = np.random.choice(185, 32, replace=False)
    Q_sub = Qn[idx]
    
    if np.linalg.cond(Q_sub) > 1e10:
        continue
    
    # Null space
    U, S, Vt = np.linalg.svd(Q_sub)
    t = Vt[-1]
    
    # Check sign
    if np.any(Qn @ t < -1e-6):
        t = -t
    if not np.all(Qn @ t > -1e-6):
        continue
    
    n_active = np.sum(np.abs(Qn @ t) < 1e-6)
    
    key = tuple(np.round(t, decimals=6))
    if key not in rays_D_set:
        rays_D_set.add(key)
        rays_D.append(t)
        if len(rays_D) <= 10:
            print(f"  Ray {len(rays_D)}: active={n_active}")

print(f"  Method D: {len(rays_D)} unique rays (from {n_trials} trials)")
if len(rays_D) > 0:
    R = np.array(rays_D)
    print(f"  Rank: {np.linalg.matrix_rank(R)}/{len(rays_D)}")
    all_rays['D'] = R

# ===== Method E: Dual Cone =====
print("\n" + "=" * 60)
print("方法 E: Dual Cone (對偶錐頂點)")
print("=" * 60)
# 對偶錐 C* = cone generated by rows of Qn
# 極端射線 = 185 個 rows 入面嘅 minimal generating set
# 每個 dual extreme ray 對應一個 Kähler cone facet

# 用 QR 找出 32 個最獨立嘅 rows
# 呢 32 個 rows 生成 C*
# 每個 row 嘅 facet normal = Kähler cone extreme ray

# 用 32 個最獨立嘅 rows
_, _, piv = scipy.linalg.qr(Qn.T, pivoting=True)
rows_32 = piv[:32]
Q_dual = Qn[rows_32]  # 32×32

# Each extreme ray of C is the null space of 31 of the 32 dual generators
rays_E = []
for k in range(32):
    # Exclude row k
    Q_excl = np.delete(Q_dual, k, axis=0)  # 31×32
    U, S, Vt = np.linalg.svd(Q_excl)
    t = Vt[-1]  # null space of the 31 rows
    
    # Check sign
    if np.any(Qn @ t < -1e-6):
        t = -t
    if not np.all(Qn @ t > -1e-6):
        continue
    
    n_active = np.sum(np.abs(Qn @ t) < 1e-6)
    rays_E.append(t)
    print(f"  Ray {len(rays_E)}: active={n_active}")

print(f"  Method E: {len(rays_E)}/32 rays")
if len(rays_E) > 0:
    R = np.array(rays_E)
    print(f"  Rank: {np.linalg.matrix_rank(R)}/{len(rays_E)}")
    all_rays['E'] = R

# ===== Cross-validation =====
print("\n" + "=" * 60)
print("交叉驗證")
print("=" * 60)

methods = list(all_rays.keys())
for i, m1 in enumerate(methods):
    for m2 in methods[i+1:]:
        R1, R2 = all_rays[m1], all_rays[m2]
        # Compute pairwise principal angles
        U1, _, _ = np.linalg.svd(R1.T, full_matrices=False)
        U2, _, _ = np.linalg.svd(R2.T, full_matrices=False)
        r1 = min(len(R1), R1.shape[1])
        r2 = min(len(R2), R2.shape[1])
        M = U1[:, :r1].T @ U2[:, :r2]
        angles = np.arccos(np.clip(np.linalg.svd(M, compute_uv=False), -1, 1))
        print(f"  {m1} vs {m2}: {len(R1)}×{len(R2)}, max angle={np.degrees(angles.max()):.2f}°")

# Combined set
if len(all_rays) > 0:
    combined = np.vstack([all_rays[m] for m in methods])
    # Deduplicate
    combined_set = set()
    combined_list = []
    for t in combined:
        key = tuple(np.round(t, decimals=6))
        if key not in combined_set:
            combined_set.add(key)
            combined_list.append(t)
    combined = np.array(combined_list)
    print(f"\n  Combined: {len(combined)} unique rays")
    print(f"  Rank: {np.linalg.matrix_rank(combined)}/{len(combined)}")
    
    # Save
    np.save(os.path.join(os.path.dirname(__file__), "..", "data", "15_all_rays.npy"), combined)
    print(f"  Saved to data/15_all_rays.npy")

print("\nDone.")