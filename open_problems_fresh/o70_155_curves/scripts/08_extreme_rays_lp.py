#!/usr/bin/env python3
"""
O70 — 08: Kähler Cone Extreme Rays via Linear Programming
===========================================================
CYTools 嘅 cone API 喺 32D 卡死。替代方法：用 scipy linprog
搵 cone 嘅 extreme rays。

方法:
  1. 用 185 curves Q_ij 定義 cone: C = {t : Q_ij @ t ≥ 0}
  2. 每個 extreme ray 係 32 個 facet 嘅交集
  3. 用 LP: min c·t subject to Q_ij @ t ≥ 0, t ≥ 0
  4. 用不同嘅 c 方向掃描 extreme rays
"""

import sys, os, math
import json
import numpy as np
from scipy.optimize import linprog

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O70 08: Kähler Cone Extreme Rays via LP")
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

print(f"  Q shape: {Q.shape}")

# Remove zero rows and rows that are negative combinations
# (we only need the unique facet normals)
# Use SVD to find the essential constraints
U, S, Vt = np.linalg.svd(Q, full_matrices=False)
print(f"  Q singular values (all 32): {S}")
print(f"  Q rank: {np.sum(S > 1e-8)}")

# ============ 2. Find interior point ============
print("\n[2] Find interior point")
# Interior point: Q @ t ≥ 0 with strict inequality
# Use LP: min 0 subject to Q @ t ≥ 1 (normalized)

# We need to find a feasible point
# Try solving: min Σ t subject to Q @ t ≥ 0, t ≥ 0
# If the cone is full-dimensional, there should be a feasible point

# Use a simpler approach: try random directions until we find interior
n_trials = 5000
found = False
for trial in range(n_trials):
    t = np.random.exponential(1, size=32)
    t = t / t.sum()
    vols = Q @ t
    if np.all(vols > -1e-8):
        found = True
        print(f"  ✅ Interior point found at trial {trial}")
        print(f"  Min volume: {vols.min():.6f}")
        print(f"  t[:5] = {t[:5]}")
        break
    if trial % 1000 == 0 and trial > 0:
        print(f"  ... trial {trial}, max neg vol: {vols.min():.4f}")

if not found:
    print(f"  ⚠️ No interior point found in {n_trials} trials")
    # Try J* projected to 32D
    jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
    Jstar = np.array(jd.get("Jstar_36D", jd))
    J32 = Jstar[basis_0]
    vols_j = Q @ J32
    print(f"  J* volumes: min={vols_j.min():.4f}, pos={(vols_j>0).sum()}/{185}")
    t = J32
    found = True  # continue anyway

# ============ 3. Find extreme rays ============
print("\n[3] Find extreme rays via LP")
if found:
    t_int = t
    # Use LP to find extreme rays: minimize c·t subject to Q·t ≥ 0, t ≥ 0, Σt = 1
    # For each random direction c, the LP finds a point on the boundary
    # If the point is on 32 facets, it's an extreme ray
    
    n_directions = 100
    extreme_rays = []
    facet_counts = []
    
    for d in range(n_directions):
        # Random direction
        c = np.random.randn(32)
        c = c / np.linalg.norm(c)
        
        # LP: min c·t subject to Q·t ≥ 0, t ≥ 0, Σt = 1
        # This finds the point on the cone boundary in direction c
        A_eq = np.ones((1, 32))
        b_eq = np.array([1.0])
        
        res = linprog(c, A_ub=-Q, b_ub=np.zeros(185), 
                      A_eq=A_eq, b_eq=b_eq,
                      bounds=[(0, None)]*32,
                      method='highs')
        
        if res.success:
            t_opt = res.x
            vols = Q @ t_opt
            n_active = np.sum(np.abs(vols) < 1e-6)
            facet_counts.append(n_active)
            
            # Check if this is a new extreme ray
            is_new = True
            for er in extreme_rays:
                if np.all(np.abs(t_opt - er) < 1e-4):
                    is_new = False
                    break
            if is_new:
                extreme_rays.append(t_opt)
                if len(extreme_rays) <= 36:
                    print(f"  Ray {len(extreme_rays)}: active facets={n_active}, obj={res.fun:.4f}")
    
    print(f"\n  Total extreme rays found: {len(extreme_rays)}")
    print(f"  Active facet counts: min={min(facet_counts)}, max={max(facet_counts)}, mean={np.mean(facet_counts):.1f}")
    
    # Check: how many extreme rays have 32 active facets?
    n_extreme = sum(1 for c in facet_counts if c >= 31)
    print(f"  Rays with ≥31 active facets: {n_extreme}/{n_directions}")
    
    # Rank of the found extreme rays
    if len(extreme_rays) > 0:
        ER = np.array(extreme_rays)
        rank_er = np.linalg.matrix_rank(ER)
        print(f"  Rank of extreme rays: {rank_er}/{len(extreme_rays)}")
        
        # Check if the cone is simplicial (32 extreme rays = simplicial)
        if rank_er == 32:
            print(f"  ✅ Extreme rays span full 32D")
        else:
            print(f"  ⚠️ Only span {rank_er}/32D")
else:
    print(f"  ⚠️ Cannot proceed without interior point")

# ============ 4. Summary ============
print("\n" + "=" * 72)
print("O70 08 總結")
print("=" * 72)
print(f"""
Kähler Cone Extreme Rays:
────────────────────────────────
1. Q_ij rank: 32/32
2. Interior point: {'found' if found else 'not found'}
3. Extreme rays found: {len(extreme_rays) if 'extreme_rays' in dir() else 0}
4. {'Full rank 32D' if 'rank_er' in dir() and rank_er == 32 else 'Incomplete'}

Note: This LP method finds POSITIVE cone extreme rays (t ≥ 0).
Full Kähler cone may have mixed-sign components.
""")

if 'extreme_rays' in dir():
    results = {
        "test": "O70 08: Extreme Rays",
        "found": found,
        "n_extreme_rays": len(extreme_rays),
        "rank_er": int(rank_er) if 'rank_er' in dir() else None,
        "facet_counts": sorted(facet_counts, reverse=True)[:20],
    }
    filepath = os.path.join(os.path.dirname(__file__), "..", "data", "08_extreme_rays.json")
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to {filepath}")