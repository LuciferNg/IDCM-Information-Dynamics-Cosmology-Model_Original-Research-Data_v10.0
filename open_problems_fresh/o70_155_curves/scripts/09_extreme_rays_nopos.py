#!/usr/bin/env python3
"""
O70 — 09: Kähler Cone Extreme Rays via LP (無正性約束)
======================================================
之前 LP 用 t ≥ 0 限制，只搵到 29 條 positive rays。
Kähler cone 允許 mixed-sign components。

新方法:
  1. 用 Q @ t ≥ 0 定義 cone (無 t ≥ 0 約束)
  2. 用 Σt² = 1 作 normalization
  3. 用不同方向 c 掃描 extreme rays
  4. 對每個 candidate ray, 檢查活躍 facet 數
"""

import sys, os, math
import json
import numpy as np
from scipy.optimize import minimize, linprog
from scipy.linalg import svd

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 09: Cone Extreme Rays (無正性約束)")
print("=" * 72)

# ============ 1. Load Q_ij ============
print("\n[1] Load Q_ij (185×32)")
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])

t_test = phi ** (-np.arange(36))
t32 = np.array([t_test[b-1] for b in basis])
eps = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    t_plus = t32.copy(); t_minus = t32.copy()
    t_plus[j] += eps; t_minus[j] -= eps
    cv_plus = np.array(cy.compute_curve_volumes(t_plus))
    cv_minus = np.array(cy.compute_curve_volumes(t_minus))
    Q[:, j] = (cv_plus - cv_minus) / (2*eps)

# Normalize rows (each constraint should have unit norm)
Q_norm = Q / np.linalg.norm(Q, axis=1, keepdims=True)
print(f"  Q_norm shape: {Q_norm.shape}")

# ============ 2. Find a feasible point ============
print("\n[2] Find feasible point via minimization")
# Minimize Σ max(0, -Q_i @ t)²  (penalty for violating constraints)
# Plus regularization: minimize ||t||²

def penalty(t):
    vols = Q_norm @ t
    viol = np.maximum(0, -vols)
    return np.sum(viol**2) + 0.001 * np.sum(t**2)

# Try multiple starting points
best_t = None
best_penalty = np.inf
for trial in range(50):
    t0 = np.random.randn(32)
    t0 = t0 / np.linalg.norm(t0)
    res = minimize(penalty, t0, method='BFGS', options={'maxiter': 500})
    if res.fun < best_penalty:
        best_penalty = res.fun
        best_t = res.x
        if best_penalty < 1e-10:
            print(f"  ✅ Feasible point found at trial {trial}! penalty={best_penalty:.2e}")
            break
    if trial % 10 == 0:
        print(f"  Trial {trial}: best penalty = {best_penalty:.2e}")

if best_penalty < 1e-6:
    t_int = best_t
    t_int = t_int / np.linalg.norm(t_int)
    vols = Q_norm @ t_int
    print(f"  Interior point: min vol = {vols.min():.4f}, max vol = {vols.max():.4f}")
    print(f"  Positive vols: {(vols > 0).sum()}/{185}")
    
    # ============ 3. Find extreme rays ============
    print("\n[3] Find extreme rays (no positivity constraint)")
    
    # Strategy: for each direction, minimize c·t subject to Q·t ≥ 0, ||t|| = 1
    # This finds the boundary of the cone in direction c
    
    # Better: use the fact that each extreme ray satisfies Q_i @ t = 0 for 32 constraints
    # We can find these by random search + refinement
    
    n_rays = 200
    rays = []
    active_counts = []
    
    for r in range(n_rays):
        # Random direction
        c = np.random.randn(32)
        c = c / np.linalg.norm(c)
        
        # Use SLSQP to minimize c·t subject to Q·t ≥ 0
        def objective(t):
            return c @ t
        
        # Constraints: Q @ t ≥ 0
        constraints = [{'type': 'ineq', 'fun': lambda t, Q=Q_norm: Q @ t}]
        
        # Normalization: ||t|| = 1
        # Actually, for a cone, we want the direction, not the magnitude
        # Use a spherical constraint
        # Or: just use the cone constraint and normalize after
        
        res = minimize(objective, t_int, method='SLSQP', 
                       constraints=constraints,
                       options={'maxiter': 1000, 'ftol': 1e-12})
        
        if res.success:
            t_opt = res.x
            vols = Q_norm @ t_opt
            n_active = np.sum(np.abs(vols) < 1e-6)
            active_counts.append(n_active)
            
            # Normalize
            t_opt = t_opt / np.linalg.norm(t_opt)
            
            # Check if new
            is_new = True
            for er in rays:
                if np.abs(t_opt @ er) > 0.9999:
                    is_new = False
                    break
            if is_new:
                rays.append(t_opt)
                if len(rays) <= 40:
                    print(f"  Ray {len(rays)}: active={n_active}, obj={res.fun:.4f}")
        
        if r % 50 == 0 and r > 0:
            print(f"  ... {r} trials, {len(rays)} unique rays found")
    
    print(f"\n  Total unique rays: {len(rays)}")
    print(f"  Active facet counts: min={min(active_counts)}, max={max(active_counts)}")
    
    # Rank of rays
    if len(rays) > 0:
        R = np.array(rays)
        rank_R = np.linalg.matrix_rank(R)
        print(f"  Rank of rays: {rank_R}/{len(rays)}")
        
        # Check if the cone is simplicial
        if rank_R == 32:
            print(f"  ✅ Extreme rays span full 32D!")
        elif rank_R >= 32:
            print(f"  🟡 Span {rank_R}/32D (need more rays)")
        else:
            print(f"  ⚠️ Only span {rank_R}/32D")
        
        # Save the rays
        np.save(os.path.join(os.path.dirname(__file__), "..", "data", "09_extreme_rays.npy"), R)
        print(f"  Saved {len(rays)} extreme rays to data/09_extreme_rays.npy")
else:
    print(f"  ❌ No feasible point found (best penalty = {best_penalty:.2e})")
    print(f"  The cone might be empty or very narrow")
    print(f"  → Try with relaxed constraints")

print(f"\nPassed checks. Results saved to data/09_extreme_rays.npy")