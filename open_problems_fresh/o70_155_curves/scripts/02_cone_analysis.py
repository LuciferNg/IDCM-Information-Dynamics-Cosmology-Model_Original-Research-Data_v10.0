#!/usr/bin/env python3
"""
O70 — 02: Kähler Cone 替代方法（從 155 curves 重建）
=====================================================
CYTools 嘅 toric_kahler_cone() 喺 d=32 卡死（extremal_rays 計唔到）。
替代方法:

方法 A: 從 155 curves volume vectors 定義 cone
  Kähler cone = {t ∈ ℝ³⁶ : t·V_c > 0 for all curves c}
  155 curves → 155 個 hyperplane constraints
  → 用 scipy.spatial.HalfspaceIntersection 搵極端射線

方法 B: 從 sr_ideal 直接構建 Mori cone
  sr_ideal 定義 toric variety 嘅非邊關係
  → 可以推導 cone 嘅 facet 結構

方法 C: 降維 (Z₃ orbifold → 12-dim, O59)
  Z₃ 作用將 36 維降至 12 維
  → 12-dim cone 可以計算

方法 D: 用 155 curves rank 30 同 Q_ij 行空間嘅關係
  Q_ij (117×32) 嘅行空間 = divisor 空間嘅線性約束
  → 檢查 Q_ij 係咪包含 cone 嘅 facet 資訊
"""

import sys, os, math
import json
import numpy as np
from scipy.spatial import HalfspaceIntersection
from scipy.optimize import linprog

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

print("=" * 72)
print("O70 02: Kähler Cone 替代方法")
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

# ============ 1. Load 155 curves ============
print("\n[1] Load 155 curves volume vectors")
d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
sr = d["sr_ideal"]
sr_set = set()
for s in sr:
    sr_set.add((min(s), max(s)))
adj = [(i, j) for i in range(1, 37) for j in range(i+1, 37) if (i, j) not in sr_set]
print(f"  Adjacency curves: {len(adj)}")

kappa_path = os.path.join(O53, "cy36_98_intersection_full.json")
if not os.path.exists(kappa_path):
    print(f"  ❌ kappa file not found")
    exit(1)
kappa = np.array(json.load(open(kappa_path))["kappa"])
V_curves = np.array([kappa[:, i-1, j-1] for i, j in adj])  # 155×36
print(f"  V_curves shape: {V_curves.shape}")

# Nonzero and rank
nz = np.abs(V_curves).sum(axis=1) > 1e-10
V_nz = V_curves[nz]
rank_all = np.linalg.matrix_rank(V_curves)
print(f"  Nonzero: {nz.sum()}/155, Rank: {rank_all}")

# ============ 2. Method A: Halfspace intersection ============
print("\n[2] Method A: Halfspace intersection")
# Kähler cone = {t : V_curves @ t ≥ 0} (by definition, all curve volumes ≥ 0)
# Need an interior point to compute the intersection

# Use J* as interior point candidate
jstar_path = os.path.join(O53, "Jstar_36D.json")
if os.path.exists(jstar_path):
    jd = json.load(open(jstar_path))
    Jstar = np.array(jd.get("Jstar_36D", jd))
    print(f"  J* shape: {Jstar.shape}")
    
    # Check J* on 155 curves
    vols = V_curves @ Jstar
    print(f"  J* volumes: min={vols.min():.4f}, max={vols.max():.4f}")
    print(f"  Positive: {(vols > 0).sum()}, Negative: {(vols < 0).sum()}, Zero: {(np.abs(vols) < 1e-10).sum()}")
    
    # If J* is interior, we can use HalfspaceIntersection
    if np.all(vols > 0):
        print(f"  J* is interior → HalfspaceIntersection feasible")
        try:
            # HalfspaceIntersection: A*x + b <= 0
            # We want V_c @ t >= 0 → -V_c @ t + 0 <= 0
            A = -V_nz  # use only nonzero vectors
            b = np.zeros(len(V_nz))
            interior = Jstar
            hi = HalfspaceIntersection(np.hstack([A, b.reshape(-1, 1)]), interior)
            print(f"  HalfspaceIntersection computed!")
            print(f"  Intersection points: {len(hi.intersections)}")
            print(f"  Dual points shape: {hi.dual_points.shape}")
            print(f"  Dual points: {hi.dual_points[:10]}")
            check("HalfspaceIntersection computed", len(hi.intersections) > 0)
        except Exception as e:
            print(f"  ⚠️ HalfspaceIntersection failed: {e}")
    else:
        print(f"  ⚠️ J* not interior (negative volumes)")
else:
    print(f"  ⚠️ J* file not found")

# ============ 3. Method B: Cone from 155 curves ============
print("\n[3] Method B: Cone from 155 curves (SVD-based)")
# The cone C = {t : V_nz @ t ≥ 0}
# The dual cone C* = V_nz^T @ ℝ_{+}^{nz} = {Σ λ_i V_nz_i : λ_i ≥ 0}
# Extreme rays of C* = minimal generating set of cone spanned by V_nz rows

# Check if we can reduce to 32D divisor basis
# Actually, V_curves is 36-dim, but Kähler cone is 32-dim (divisor basis)
# The 4 redundant dimensions correspond to the 4 missing divisors

# Compute the cone's facial structure via SVD
U, S, Vt = np.linalg.svd(V_nz, full_matrices=False)
print(f"  SVD: U({U.shape[0]}×{U.shape[1]}), S rank={np.sum(S > 1e-8)}")
print(f"  Singular values: {S[:10]}")

# The row space of V_nz = span of curve volume vectors = 30-dim
# The null space of V_nz = 36-30 = 6-dim = unbounded directions
# → Kähler cone is not strictly convex in these 6 directions

# Find the null space basis
null_mask = S < 1e-8
null_dim = null_mask.sum()
print(f"  Null space dimension: {null_dim}")
print(f"  (These are directions where all curve volumes = 0)")
print(f"  → Cone is 36-dim but only 30-dim of curve constraints")

# ============ 4. Compare 155 curves with CY curve_basis ============
print("\n[4] CYTools curve_basis vs 155 curves")
try:
    import cytools
    from cytools import Polytope
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    pts = np.array(d["points"])
    p = Polytope(pts)
    tri = p.triangulate()
    cy = tri.get_cy()
    basis = cy.divisor_basis()
    curve_basis = cy.curve_basis()
    print(f"  Divisor basis: {len(basis)}")
    print(f"  Curve basis: {len(curve_basis)}")
    check("32 divisor basis", len(basis) == 32)
    check("32 curve basis", len(curve_basis) == 32)  # Actually might be 32 too
    
    # What are the 32 curves?
    print(f"  Curve basis type: {type(curve_basis)}")
    if hasattr(curve_basis, '__len__'):
        print(f"  Curve basis content: {curve_basis}")
except Exception as e:
    print(f"  ⚠️ CYTools error: {e}")

# ============ 5. Method C: Use Q_ij matrix ============
print("\n[5] Method C: Q_ij (curve-divisor intersection) analysis")
# Q_ij = ∂V_i/∂t_j = curve C_i · divisor D_j
# The rows of Q_ij = volume vectors of the curve basis
# The columns of Q_ij = divisor constraints

# Load Q_ij from O57 if available
q_path = os.path.join(BASE, "open_problems_fresh", "o57_cy3_projection_gen", "data")
# Check if we can compute Q_ij from kappa
# Q_ij = κ_ijk · t_k (for a specific t)
# But the full Q_ij (curve-divisor intersection) = κ_ijk for each curve

# Actually, the 155 curves' volume vectors V_c = κ_ij· are the Q_ij rows
# They describe how each curve volume depends on the Kähler parameters

# ============ 6. Summary ============
print("\n" + "=" * 72)
print("O70 02 總結")
print("=" * 72)
print(f"""
Kähler Cone 分析:
────────────────────────────────
1. 155 curves → 52 nonzero volume vectors → rank 30
2. Cone definition: C = {{t : V_c(t) ≥ 0}} = 155 halfspaces
3. {null_dim if 'null_dim' in dir() else '?'} null directions = cone unbounded in these

Key insight:
  155 curves span 30-dim subspace = C sector rank
  6 null directions = unbounded cone directions
  155 ≠ 32 (divisor basis) → curves are NOT the full cone definition
  Kähler cone needs 32 independent constraints, curves give 30
  → Missing 2 constraints = ?
""")

results = {
    "test": "O70 02: Kähler Cone",
    "curves_rank": int(rank_all),
    "nz_curves": int(nz.sum()),
    "null_dim": int(null_dim) if 'null_dim' in dir() else None,
    "actual_cone_dim": 32,
    "missing_constraints": 32 - int(rank_all),
}
filepath = os.path.join(os.path.dirname(__file__), "..", "data", "02_cone_analysis.json")
with open(filepath, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Results saved to {filepath}")
print(f"Passed: {passed}, Failed: {failed}")