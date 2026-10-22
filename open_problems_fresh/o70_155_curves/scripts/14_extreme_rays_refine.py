#!/usr/bin/env python3
"""
O70 — 14: Extreme Rays — Active Constraint Refinement
=======================================================
1. LP 搵 boundary point
2. 找出 active constraints
3. 用 QR 挑 32 個獨立嘅 active constraints
4. 解 32×32 system → extreme ray
5. 驗證: Q @ t ≥ 0
"""

import sys, os, math, json, numpy as np
import scipy.linalg
from scipy.optimize import minimize
import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 14: Extreme Rays — Active Constraint Refinement")
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

Qn = Q / np.linalg.norm(Q, axis=1, keepdims=True)
print(f"Q: {Q.shape}, rank: {np.linalg.matrix_rank(Q)}")

def find_boundary_point(c):
    """Find a point on the cone boundary in direction c."""
    def obj(t):
        return c @ t
    cons = [{'type': 'ineq', 'fun': lambda t: Qn @ t},
            {'type': 'eq', 'fun': lambda t: np.sum(t**2) - 1.0}]
    t0 = np.random.randn(32)
    t0 = t0 / np.linalg.norm(t0)
    res = minimize(obj, t0, method='SLSQP', constraints=cons,
                   options={'maxiter': 2000, 'ftol': 1e-12})
    if res.success:
        return res.x
    return None

def refine_to_extreme_ray(t_boundary, tol=1e-6):
    """Given a boundary point, find the extreme ray it lies on."""
    # Find active constraints
    vols = Qn @ t_boundary
    active = np.where(np.abs(vols) < tol)[0]
    
    if len(active) < 32:
        return None, 0  # Not enough constraints
    
    # Find 32 linearly independent active constraints
    Q_active = Qn[active]  # n_active × 32
    
    # Use QR with pivoting on the rows of Q_active
    # We want to find 32 rows that are linearly independent
    # QR on Q_active.T (32 × n_active) with column pivoting
    # gives us the n_active columns of Q_active.T that are independent
    # = n_active rows of Q_active
    _, R, piv = scipy.linalg.qr(Q_active.T, pivoting=True)
    # piv[:32] gives indices of 32 independent rows of Q_active
    # (relative to the `active` array, not the full Q)
    n_indep = min(32, len(piv))
    if n_indep < 32:
        return None, 0
    
    # Get the 32 independent rows
    Q_32 = Q_active[piv[:32]]  # 32×32
    
    if np.linalg.cond(Q_32) > 1e10:
        return None, 0
    
    # The extreme ray is the null space of Q_32 (1D)
    U, S, Vt = np.linalg.svd(Q_32)
    t_ray = Vt[-1]  # last singular vector = null direction
    
    # Check sign
    if np.any(Qn @ t_ray < -1e-6):
        t_ray = -t_ray
    
    # Verify
    if not np.all(Qn @ t_ray > -1e-6):
        return None, 0
    
    # Count how many constraints are actually tight
    n_active_final = np.sum(np.abs(Qn @ t_ray) < 1e-6)
    
    return t_ray, n_active_final

# Find extreme rays
n_trials = 500
rays = []
rays_set = set()
debug_info = {"n_boundary": 0, "n_active_ge_32": 0, "n_independent": 0, "n_valid": 0}

for trial in range(n_trials):
    # Random direction
    c = np.random.randn(32)
    c = c / np.linalg.norm(c)
    
    # Find boundary point
    t_b = find_boundary_point(c)
    if t_b is None:
        continue
    debug_info["n_boundary"] += 1
    
    # Count active constraints
    vols = Qn @ t_b
    n_active = np.sum(np.abs(vols) < 1e-6)
    if n_active < 32:
        continue
    debug_info["n_active_ge_32"] += 1
    
    # Use SVD of ALL active constraints to find null space
    Q_active = Qn[np.where(np.abs(vols) < 1e-6)[0]]  # n_active × 32
    try:
        U, S, Vt = np.linalg.svd(Q_active, full_matrices=False)
    except:
        continue
    rank_active = np.sum(S > 1e-8)
    if rank_active < 32:
        continue
    debug_info["n_independent"] += 1
    
    # The null space of Q_active: if rank_active = 32, the null space
    # is the last (n_active - 32) singular vectors of Vt
    # The most null-like direction is Vt[-1]
    t_ray = Vt[-1]  # minimizes ||Q_active @ t||
    
    # Check sign
    if np.any(Qn @ t_ray < -1e-6):
        t_ray = -t_ray
    if not np.all(Qn @ t_ray > -1e-6):
        continue
    
    debug_info["n_valid"] += 1
    n_active_final = np.sum(np.abs(Qn @ t_ray) < 1e-6)
    
    # Check if new (use hash of rounded values)
    key = tuple(np.round(t_ray, decimals=6))
    if key not in rays_set:
        rays_set.add(key)
        rays.append(t_ray)
        if len(rays) <= 35:
            print(f"Ray {len(rays)}: active={n_active_final}")
    
    if trial % 200 == 199:
        print(f"... trial {trial+1}, {len(rays)} extreme rays")

print(f"\nTotal extreme rays: {len(rays)}")
print(f"Debug: {debug_info}")
if len(rays) > 0:
    R = np.array(rays)
    rank_R = np.linalg.matrix_rank(R)
    print(f"Rank: {rank_R}/{len(rays)}")
    
    if rank_R == 32:
        print("✅ Full 32D cone spanned!")
    elif rank_R >= 32:
        print(f"🟡 Span {rank_R}/32D")
    else:
        print(f"⚠️ Only span {rank_R}/32D")
    
    np.save(os.path.join(os.path.dirname(__file__), "..", "data", "14_extreme_rays.npy"), R)
    print(f"Saved to data/14_extreme_rays.npy")
else:
    print("No extreme rays found. Debug info suggests the approach needs refinement.")