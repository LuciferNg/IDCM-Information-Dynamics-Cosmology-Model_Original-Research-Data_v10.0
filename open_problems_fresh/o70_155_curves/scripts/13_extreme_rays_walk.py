#!/usr/bin/env python3
"""
O70 — 13: Extreme Rays via LP Boundary Walk
=============================================
1. LP 搵 cone boundary 上一點
2. 找出 active constraints
3. 用 active constraints 解出 extreme ray
4. 重複用不同方向掃描
"""

import sys, os, math, json, numpy as np
from scipy.optimize import minimize, linprog
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 13: Extreme Rays via LP Boundary Walk")
print("=" * 72)

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

# Normalize rows
Qn = Q / np.linalg.norm(Q, axis=1, keepdims=True)

print(f"Q shape: {Q.shape}, rank: {np.linalg.matrix_rank(Q)}")

# Strategy: find extreme rays by solving LP with random objectives
# minimize c·t s.t. Q·t ≥ 0, t·t = 1 (on sphere)
# The optimum is at a boundary point. If the boundary point has
# 32 active constraints, it's an extreme ray.

# Use SLSQP which handles nonlinear constraints
def find_extreme_ray(c, t0, tol_active=1e-6):
    """Find extreme ray in direction c using minimization."""
    # Objective: minimize c·t on the sphere
    def obj(t):
        return c @ t
    
    # Constraints: Q·t ≥ 0
    constraints = [{'type': 'ineq', 'fun': lambda t, Q=Qn: Qn @ t}]
    
    # Normalization: ||t|| = 1
    constraints.append({'type': 'eq', 'fun': lambda t: np.sum(t**2) - 1.0})
    
    res = minimize(obj, t0, method='SLSQP', constraints=constraints,
                   options={'maxiter': 2000, 'ftol': 1e-12})
    
    if not res.success:
        return None, 0
    
    t = res.x
    vols = Qn @ t
    active = np.where(np.abs(vols) < tol_active)[0]
    n_active = len(active)
    
    return t, n_active

# Try many random directions
n_trials = 500
rays = []
active_counts = []

for trial in range(n_trials):
    c = np.random.randn(32)
    c = c / np.linalg.norm(c)
    t0 = np.random.randn(32)
    t0 = t0 / np.linalg.norm(t0)
    
    t, n_active = find_extreme_ray(c, t0)
    if t is None:
        continue
    
    active_counts.append(n_active)
    
    # Check if new
    is_new = True
    for r in rays:
        if np.abs(r @ t) > 0.9999:
            is_new = False
            break
    if is_new:
        rays.append(t)
        if len(rays) <= 35:
            print(f"Ray {len(rays)}: active={n_active}, c@t={c@t:.4f}")

    if trial % 100 == 99:
        print(f"  ... trial {trial+1}, {len(rays)} unique rays, mean active={np.mean(active_counts):.1f}")

print(f"\nTotal unique rays: {len(rays)}")
print(f"Active counts: min={min(active_counts)}, max={max(active_counts)}, mean={np.mean(active_counts):.1f}")

if len(rays) > 0:
    R = np.array(rays)
    rank_R = np.linalg.matrix_rank(R)
    print(f"Rank of rays: {rank_R}/{len(rays)}")
    
    # Count how many have ≥32 active constraints (true extreme rays)
    n_extreme = sum(1 for c in active_counts if c >= 32)
    print(f"Rays with ≥32 active constraints: {n_extreme}/{n_trials}")
    
    # Save
    np.save(os.path.join(os.path.dirname(__file__), "..", "data", "13_extreme_rays.npy"), R)
    print(f"Saved {len(rays)} rays to data/13_extreme_rays.npy")

print("Done.")