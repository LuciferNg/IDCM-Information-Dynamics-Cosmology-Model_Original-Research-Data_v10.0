#!/usr/bin/env python3
"""
O70 — 07: 185 總 Curves 分析（_compute_curve_volumes 嘅 30 條額外 curves）
======================================================================
已知:
  - 155 adjacency curves (sr_ideal complement among 36 divisor points)
  - 185 total curves from CYTools compute_curve_volumes
  - 185 - 155 = 30 = 2L₅+2B = rank(155 curves)

問題: 30 條額外 curves 係咩?
  1. 涉及 12 個 uninvolved points (0, 37-47)?
  2. 係咪 cone 嘅 facet 定義者?
  3. 同 4 missing divisors [3,4,7,8] 嘅關係?
"""

import sys, os, math
import json
import numpy as np
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

print("=" * 72)
print("O70 07: 185 總 Curves 分析")
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

import cytools
from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# ============ 1. Load CYTools ============
print("\n[1] Load CYTools")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"])
p = Polytope(pts)
tri = p.triangulate()
cy = tri.get_cy()
basis = cy.divisor_basis()
basis_0 = np.array([b-1 for b in basis])
print(f"  Divisor basis: {len(basis)}")

# ============ 2. Compute all 185 curve volumes ============
print("\n[2] All 185 curve volumes")
# Use a test Kähler parameter
t_test = phi ** (-np.arange(36))
t32 = np.array([t_test[b-1] for b in basis])
cv_all = np.array(cy.compute_curve_volumes(t32))
print(f"  Total curves: {len(cv_all)}")
check("185 total curves", len(cv_all) == 185, f"({len(cv_all)})")

# CYTools curve_basis
curve_basis = cy.curve_basis()
print(f"  Curve basis: {len(curve_basis)} → {curve_basis}")

# ============ 3. Try to identify the 30 extra curves ============
print("\n[3] Identify the 30 extra curves beyond adjacency")
sr_set = set()
for s in d["sr_ideal"]:
    sr_set.add((min(s), max(s)))
adj = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if (i, j) not in sr_set]

# The 185 curves from CYTools are indexed by the curve_basis
# Each curve in the basis can be a linear combination of the 155 adjacency curves
# Or they might be different curves entirely

# Let's check: how many of the 185 curves are among the 32 curve_basis?
# The curve_basis has 32 indices — these are the "generators" of the Mori cone
# The 185 curves are all the curves in the toric variety
# Each curve is a positive combination of the 32 basis curves

# Actually, compute_curve_volumes returns volumes for ALL curves
# But these curves are indexed differently from the adjacency pairs

# Let's try to identify the 155 adjacency curves among the 185
# We can check: for each adjacency pair (i,j), what is the volume?
# The volume of curve C_ij = Σ_k κ_ijk · t_k

# We can compute volumes for the 155 adjacency curves and compare
kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json"))).get("kappa"))
V_adj = np.array([kappa[:, i-1, j-1] @ t_test for i, j in adj])  # 155 volumes

# Compare with cv_all
# Find which cv_all entries match the adjacency volumes
# (with rounding since they might differ slightly)
print(f"  Adjacency volumes at t: {V_adj[:10]}")
print(f"  CYTools volumes at t: {cv_all[:10]}")

# Check: are the adjacency volumes a subset of the CYTools volumes?
# Sort both and compare
adj_sorted = np.sort(V_adj)
cv_sorted = np.sort(cv_all)
print(f"  Adj volume range: [{V_adj.min():.4f}, {V_adj.max():.4f}]")
print(f"  CV all range: [{cv_all.min():.4f}, {cv_all.max():.4f}]")

# Count how many adjacency volumes match CYTools volumes
# (within tolerance)
matches = 0
for v in V_adj:
    if np.any(np.abs(cv_all - v) < 1e-6):
        matches += 1
print(f"  Adjacency volumes found in CYTools: {matches}/155")

# The 30 extra curves: which ones are they?
# Let's compute the 185 × 32 volume matrix using numerical differentiation
# Q_ij = ∂V_i/∂t_j
print("\n  Computing Q_ij (185×32) via numerical differentiation...")
eps = 1e-5
Q = np.zeros((185, 32))
for j in range(32):
    t_plus = t32.copy()
    t_minus = t32.copy()
    t_plus[j] += eps
    t_minus[j] -= eps
    cv_plus = np.array(cy.compute_curve_volumes(t_plus))
    cv_minus = np.array(cy.compute_curve_volumes(t_minus))
    Q[:, j] = (cv_plus - cv_minus) / (2*eps)

print(f"  Q shape: {Q.shape}")
rank_Q = np.linalg.matrix_rank(Q)
print(f"  Rank(Q) = {rank_Q}")
check("Q rank = ?", rank_Q > 0, f"({rank_Q})")

# SVD of Q
U, S, Vt = np.linalg.svd(Q, full_matrices=False)
print(f"  Q singular values (top 15): {S[:15]}")
print(f"  Q rank: {np.sum(S > 1e-8)}/32")

# Check: does Q span the full 32D?
print(f"  Q spans {np.sum(S > 1e-8)}/32 dimensions")
check("Q spans full 32D?", np.sum(S > 1e-8) == 32, f"({np.sum(S > 1e-8)}/32)")

# ============ 4. Find which curves are active at J* ============
print("\n[4] Active curves at J*")
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))
Jstar_32 = np.array([Jstar[b-1] for b in basis])
cv_j = np.array(cy.compute_curve_volumes(Jstar_32))
print(f"  J* volumes: {len(cv_j)} total")
print(f"  Positive: {(cv_j > 1e-8).sum()}, Near-zero: {(np.abs(cv_j) < 1e-8).sum()}, Negative: {(cv_j < -1e-8).sum()}")

# Curves with zero volume at J* = potential facet-defining curves
zero_vol = np.abs(cv_j) < 1e-8
print(f"  Zero-volume curves at J*: {zero_vol.sum()}/185")
print(f"  → These could be the facet-defining curves")

# ============ 5. Summary ============
print("\n" + "=" * 72)
print("O70 07 總結")
print("=" * 72)
print(f"""
185 總 Curves 分析:
────────────────────────────────
1. Total curves: {len(cv_all)}
2. Curve basis: {len(curve_basis)}
3. Q_ij rank: {rank_Q}/32
4. J* zero-volume curves: {zero_vol.sum()}/185

{'✅ Q_ij spans full 32D — 185 curves contain all cone info' if np.sum(S > 1e-8) == 32 else '⚠️ Q_ij does NOT span full 32D'}
""")

results = {
    "test": "O70 07: 185 Curves",
    "total_curves": len(cv_all),
    "curve_basis": len(curve_basis),
    "Q_rank": int(rank_Q),
    "Q_rank_full": bool(np.sum(S > 1e-8) == 32),
    "jstar_zero_vol": int(zero_vol.sum()),
}
filepath = os.path.join(os.path.dirname(__file__), "..", "data", "07_185_curves.json")
with open(filepath, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Results saved to {filepath}")
print(f"Passed: {passed}, Failed: {failed}")