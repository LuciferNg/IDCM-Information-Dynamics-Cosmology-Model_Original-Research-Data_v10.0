#!/usr/bin/env python3
"""
O70 — 20: Kähler Cone Extreme Rays via pypoman (cddlib)
=========================================================
使用 pypoman (pycddlib) 計算 32D Kähler cone 嘅 extreme rays。
"""
import sys, os, math, json, numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 20: Kähler Cone Extreme Rays — pypoman")
print("=" * 72)

# Load data
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()
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
print(f"Q: 185×32, rank: {np.linalg.matrix_rank(Q)}")

# Use pypoman to compute extreme rays
# The cone is C = {x : Qn @ x ≥ 0}
# pypoman expects inequalities in the form A @ x + b ≥ 0
# So A = Qn, b = 0

from pypoman import compute_extreme_rays

print("\nComputing extreme rays via pypoman...")
# compute_extreme_rays takes A, b where A @ x + b ≥ 0
# Returns the extreme rays of the cone
rays = compute_extreme_rays(Qn, np.zeros(185))

print(f"Found {len(rays)} extreme rays")

if len(rays) > 0:
    R = np.array(rays)
    print(f"Rays: {R.shape}")
    print(f"Rank: {np.linalg.matrix_rank(R)}")
    
    # Check cone membership
    in_cone = 0
    for r in R:
        if np.all(Qn @ r > -1e-6):
            in_cone += 1
    print(f"Rays in cone: {in_cone}/{len(rays)}")
    
    # Active constraints
    active_counts = [np.sum(np.abs(Qn @ r) < 1e-6) for r in R]
    print(f"Active: min={min(active_counts)}, max={max(active_counts)}, mean={np.mean(active_counts):.1f}")
    print(f"Rays with ≤35 active: {sum(1 for c in active_counts if c <= 35)}")
    print(f"Rays with ≤40 active: {sum(1 for c in active_counts if c <= 40)}")
    print(f"Rays with ≤50 active: {sum(1 for c in active_counts if c <= 50)}")
    
    # Save
    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "20_pypoman_rays.npy")
    np.save(out_path, R)
    print(f"Saved to {out_path}")
    
    # Cross-validate with LP method
    R_lp = np.load(os.path.join(os.path.dirname(__file__), "..", "data", "15_all_rays.npy"))
    # Check if pypoman rays are a subset of the cone
    # and if they span the same space
    # Principal angles
    from scipy.linalg import subspace_angles
    angles = subspace_angles(R.T, R_lp.T)
    print(f"\nCross-validation with LP method:")
    print(f"  Principal angles: {np.degrees(angles[:5])}")
    print(f"  Max angle: {np.degrees(angles.max()):.2f}°")
else:
    print("No rays found")

print("\nDone.")