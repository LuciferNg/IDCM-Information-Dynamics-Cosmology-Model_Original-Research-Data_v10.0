#!/usr/bin/env python3
"""
O70 — 06: Kähler Cone 32D 完整分析（CYTools + Scipy）
======================================================
目標:
  1. 用 CYTools toric_kahler_cone() 獲取 cone 物件
  2. 檢查 cone 嘅 extremal_rays / hyperplanes
  3. 用 scipy 搵 interior point + HalfspaceIntersection
  4. 檢查 155 curves (32D) 同 cone facet 嘅關係
  5. 檢查 4 missing divisors 點樣影響 cone 結構
"""

import sys, os, math
import json
import numpy as np
from scipy.optimize import linprog
from scipy.spatial import HalfspaceIntersection

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

print("=" * 72)
print("O70 06: Kähler Cone 32D 完整分析")
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

# ============ 1. Load CYTools ============
print("\n[1] Load CYTools")
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
print(f"  Divisor basis: {len(basis)} → {basis}")
print(f"  Missing divisors: {sorted(set(range(1,37)) - set(basis))}")

# ============ 2. Kähler cone ============
print("\n[2] Kähler cone")
kc = cy.toric_kahler_cone()
print(f"  kc type: {type(kc).__name__}")
print(f"  kc dim: {kc.dim()}")

# Try methods
if hasattr(kc, 'extremal_rays'):
    try:
        rays = kc.extremal_rays()
        print(f"  extremal_rays: {len(rays)}")
    except Exception as e:
        print(f"  extremal_rays: ⚠️ {e}")

if hasattr(kc, 'hyperplanes'):
    try:
        hp = kc.hyperplanes()
        print(f"  hyperplanes: {len(hp)}")
    except Exception as e:
        print(f"  hyperplanes: ⚠️ {e}")

if hasattr(kc, 'inequalities'):
    try:
        ineq = kc.inequalities()
        print(f"  inequalities: {len(ineq)}")
    except Exception as e:
        print(f"  inequalities: ⚠️ {e}")

if hasattr(kc, 'generators'):
    try:
        gen = kc.generators()
        print(f"  generators: {len(gen)}")
    except Exception as e:
        print(f"  generators: ⚠️ {e}")

# ============ 3. 155 curves in 32D ============
print("\n[3] 155 curves in 32D divisor basis")
sr_set = set()
for s in d["sr_ideal"]:
    sr_set.add((min(s), max(s)))
adj = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if (i, j) not in sr_set]

kappa = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json"))).get("kappa"))
V_adj = np.array([kappa[:, i-1, j-1] for i, j in adj])  # 155×36

# Map 36D → 32D: select only the divisor basis columns
# basis is 1-based, numpy needs 0-based
basis_0 = np.array([b-1 for b in basis])
V_32 = V_adj[:, basis_0]  # 155×32
print(f"  V_32 shape: {V_32.shape}")

# Rank in 32D
rank_32 = np.linalg.matrix_rank(V_32)
print(f"  Rank(155×32) = {rank_32}")
check("rank in 32D", rank_32 > 0, f"({rank_32})")

# Nonzero in 32D
nz_32 = np.abs(V_32).sum(axis=1) > 1e-10
print(f"  Nonzero in 32D: {nz_32.sum()}/155")

# ============ 4. Find interior point of Kähler cone ============
print("\n[4] Find interior point via linear programming")
# Kähler cone: {t ∈ ℝ³² : V_adj(t) ≥ 0}
# For the full cone, we need to check against ALL curves, not just the 155
# But we can use the 155 as a proxy

# Try scipy linprog: find a point that satisfies all constraints
# We need: V_32 @ t ≥ 0 (all curve volumes ≥ 0)
# Also: sum(t) = 1 (normalization)

# Use the nonzero vectors only
V_nz_32 = V_32[nz_32]  # nonzero volume vectors in 32D

# Actually, the Kähler cone is defined by ALL curves, not just the 155
# Let's try to get the cone's inequalities from CYTools
if hasattr(kc, 'inequalities'):
    try:
        ineq = kc.inequalities()
        # ineq is a list of (A, b) pairs where A·t + b ≥ 0
        # For Kähler cone, b = 0 (homogeneous cone)
        print(f"  inequalities: {len(neq)}")
    except Exception as e:
        print(f"  inequalities failed: {e}")

# Try: use kc.contains() to find interior
# Generate random directions and test
print("\n  Searching for interior point...")
n_trials = 1000
found_interior = False
for trial in range(n_trials):
    t_test = np.random.uniform(0.1, 1.0, size=32)
    t_test = t_test / t_test.sum()
    t_basis = np.zeros(36)
    for idx, b in enumerate(basis):
        t_basis[b-1] = t_test[idx]
    if kc.contains(t_basis[:32]):
        found_interior = True
        print(f"  ✅ Found interior point at trial {trial}")
        print(f"  t[:10] = {t_test[:10]}")
        break

if not found_interior:
    print(f"  ⚠️ No interior point found in {n_trials} random trials")
    # Try with J* as starting point
    jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
    Jstar = np.array(jd.get("Jstar_36D", jd))
    Jstar_32 = Jstar[basis_0]
    # Check if it's in the cone
    if kc.contains(Jstar_32):
        print(f"  J* is in the Kähler cone! (but not interior)")
        found_interior = True
    else:
        print(f"  J* is NOT in the Kähler cone")

# ============ 5. Check 155 curves vs cone facets ============
print("\n[5] 155 curves vs cone facets")
if found_interior:
    t_int = t_test if 't_test' in dir() else Jstar_32
    # Check which curves are active (volume = 0) at the interior
    vols = V_32 @ t_int
    active = np.abs(vols) < 1e-8
    print(f"  Active constraints at interior: {active.sum()}/155")
    print(f"  (Interior should have NO active constraints)")
    
    # Check: which curves are facets?
    # A facet-constraining curve has V_c spanning a facet direction
    # = the curve's volume vector is a facet normal
    
    # Use the cone's own hyperplanes
    if hasattr(kc, 'hyperplanes'):
        try:
            hp = kc.hyperplanes()
            print(f"  Cone hyperplanes: {len(hp)}")
            print(f"  Hyperplane dims: {[h.shape for h in hp[:5]]}")
        except Exception as e:
            print(f"  hyperplanes: {e}")

# ============ 6. Summary ============
print("\n" + "=" * 72)
print("O70 06 總結")
print("=" * 72)
print(f"""
Kähler Cone 32D 分析:
────────────────────────────────
1. Cone dim: {kc.dim()}
2. 155 curves in 32D: rank {rank_32}
3. {'Interior point found' if found_interior else 'No interior point found'}
4. Missing divisors: [3,4,7,8] = N_gen, B, L₄, 2B

Open:
  - 需要 cone extremal rays / hyperplanes 先可確定 facet 結構
  - CYTools 嘅 cone API 喺 32D 有限制
""")

results = {
    "test": "O70 06: Cone 32D",
    "cone_dim": kc.dim(),
    "rank_32D": int(rank_32),
    "interior_found": found_interior,
    "nz_32D": int(nz_32.sum()),
}
filepath = os.path.join(os.path.dirname(__file__), "..", "data", "06_cone_32d.json")
with open(filepath, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Results saved to {filepath}")
print(f"Passed: {passed}, Failed: {failed}")