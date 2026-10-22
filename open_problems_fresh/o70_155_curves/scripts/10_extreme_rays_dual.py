#!/usr/bin/env python3
"""
O70 — 10: Kähler Cone Extreme Rays via Mori Cone Duality
==========================================================
核心原理:
  Kähler cone = dual of Mori cone
  Mori cone extreme rays = 32 curve_basis curves
  → Kähler cone has 32 extreme rays, each dual to one curve_basis element

Method:
  For each curve c in the 32 curve_basis:
    Solve: Q_i @ t = 0 for all basis curves i ≠ c
    With:  Q_c @ t > 0 (normalization)
    This gives the Kähler cone extreme ray dual to curve c.

  Then verify that the ray satisfies ALL 185 constraints (Q @ t ≥ 0).
"""

import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 10: Extreme Rays via Mori Cone Duality")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. Load Q_ij ============
print("\n[1] Load data")
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
curve_basis = cy.curve_basis()
basis_0 = np.array([b-1 for b in basis])
print(f"  Divisor basis: {len(basis)}")
print(f"  Curve basis: {len(curve_basis)} → {curve_basis}")

# Compute Q_ij
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

# ============ 2. Identify which Q rows correspond to curve_basis ============
print("\n[2] Identify curve_basis rows in Q")
# The curve_basis gives 32 divisor indices
# But Q rows correspond to ALL 185 curves, not just the basis
# We need to find the 32 Q rows that correspond to the 32 basis curves

# The curve_basis indices are 1-based divisor indices
# The Q rows are the volume vectors for each curve
# CYTools compute_curve_volumes returns volumes for curves indexed by the Mori cone basis
# The curve_basis tells us which divisors these curves are

# For each basis curve, the Q row IS the volume vector
# But we don't know which Q row maps to which curve_basis entry

# Let's use a different approach: the curve_basis indices tell us which divisors
# are the Mori cone generators. The Q rows for these specific divisor-pair curves
# can be identified by their volume pattern.

# Actually, the curve_basis gives the 32 Mori cone generators (curves).
# Each is represented by a divisor index. The curve C_k is the curve
# corresponding to divisor k in the curve_basis.

# The Q matrix is 185×32. Each row is a curve's volume vector.
# The 32 curve_basis curves should have Q rows that are linearly independent.

# Strategy: find 32 linearly independent Q rows
U, S, Vt = np.linalg.svd(Q, full_matrices=False)
print(f"  Q rank: {np.sum(S > 1e-8)}/32")

# Find 32 independent rows using QR with column pivoting on Q^T
# Q_norm.T is 32×185. QR with pivoting finds 32 columns of Q_norm.T that are independent
# = columns of Q_norm.T = rows of Q_norm
import scipy.linalg
Q_norm = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-15)
# QR with pivoting on Q^T (32×185)
_, _, piv = scipy.linalg.qr(Q_norm.T, pivoting=True)
# The first 32 pivots are the indices of the 32 most independent columns of Q^T = rows of Q
basis_rows = piv[:32]
print(f"  Selected 32 basis Q rows: {sorted(basis_rows)}")

# Extract the 32×32 basis matrix
Q_basis = Q[basis_rows]  # 32×32
print(f"  Q_basis shape: {Q_basis.shape}")
print(f"  Q_basis condition: {np.linalg.cond(Q_basis):.2f}")
check("Q_basis invertible", np.linalg.cond(Q_basis) < 1e10, f"(cond={np.linalg.cond(Q_basis):.2f})")

# ============ 3. Compute extreme rays ============
print("\n[3] Compute extreme rays via dual cone")
# For each basis curve k, the extreme ray is the solution to:
# Q_basis_i @ t = 0 for all i ≠ k
# Q_basis_k @ t > 0

# This is equivalent to inverting Q_basis and taking each column
# Q_basis @ t = e_k → t = Q_basis^{-1} @ e_k
# where e_k is the k-th unit vector

Q_basis_inv = np.linalg.inv(Q_basis)

extreme_rays = []
for k in range(32):
    e_k = np.zeros(32)
    e_k[k] = 1.0
    t_k = Q_basis_inv @ e_k  # 32D ray
    
    # Normalize
    t_k = t_k / np.linalg.norm(t_k)
    
    # Check sign: all Q @ t_k should be ≥ 0
    vols = Q @ t_k
    all_positive = np.all(vols > -1e-8)
    
    if not all_positive:
        # Try opposite direction
        t_k = -t_k
        vols = Q @ t_k
        all_positive = np.all(vols > -1e-8)
    
    if all_positive:
        extreme_rays.append(t_k)
        n_active = np.sum(np.abs(vols) < 1e-6)
        print(f"  Ray {k}: active facets={n_active}, min vol={vols.min():.4f}")
    else:
        print(f"  Ray {k}: ❌ not in cone (min vol={vols.min():.4f})")

print(f"\n  Valid extreme rays: {len(extreme_rays)}/32")

# ============ 4. Verify ============
print("\n[4] Verify extreme rays")
if len(extreme_rays) > 0:
    R = np.array(extreme_rays)
    rank_R = np.linalg.matrix_rank(R)
    print(f"  Rank of extreme rays: {rank_R}/{len(extreme_rays)}")
    check("Full rank 32", rank_R == 32, f"({rank_R})")
    
    # Check: each ray should be on 32 facets
    for k, t_k in enumerate(extreme_rays):
        vols = Q @ t_k
        n_zero = np.sum(np.abs(vols) < 1e-6)
        if n_zero < 31:
            print(f"  Ray {k}: only {n_zero} zero facets (expected 31-32)")
    
    # Save
    np.save(os.path.join(os.path.dirname(__file__), "..", "data", "10_extreme_rays.npy"), R)
    print(f"  Saved {len(extreme_rays)} extreme rays")
    
    # Check: cone structure
    # For a simplicial cone, T = convex cone generated by extreme rays
    # Check: is every point in the cone a positive combination of rays?
    # Use the interior point
    
    # Check that the cone is full-dimensional
    if rank_R == 32:
        print(f"  ✅ Kähler cone is a {len(extreme_rays)}-ray cone in 32D")
        print(f"  → The cone is {'simplicial' if len(extreme_rays) == 32 else 'non-simplicial'}")
else:
    print(f"  ⚠️ No valid extreme rays found")
    print(f"  The Q_basis might not be the right set of constraints")

print(f"\nPassed: {passed}, Failed: {failed}")