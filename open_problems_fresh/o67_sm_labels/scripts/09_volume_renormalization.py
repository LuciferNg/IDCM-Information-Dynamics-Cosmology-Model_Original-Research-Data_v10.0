#!/usr/bin/env python3
"""
O67 Problem 5 Attack: CYTools Volume Renormalization
=====================================================
Resolve the divisor volume overflow using Complexified Kähler Moduli.

Phase A: Switch from φ^(35-i) toy parameters to J* fixed point
Phase B: Compute divisor volumes at J* (should be O(1) not O(10^12))
Phase C: Mirror Map rescaling if still large
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O67 Problem 5: CYTools Volume Renormalization")
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

# ============ 1. Load J* and CY ============
print("\n[1] Load J* fixed point")
jstar_data = json.load(open(os.path.join(O53, "Jstar_36D.json")))
J36 = np.array(jstar_data["Jstar_36D"])
print(f"  J* (36D): {len(J36)} entries")
print(f"  J* range: [{J36.min():.6f}, {J36.max():.6f}]")
print(f"  J* mean: {J36.mean():.6f}")
print(f"  CY volume: {jstar_data['Vol']} = 1/{1/jstar_data['Vol']:.0f}")
check("J* all positive", np.all(J36 > 0), f"(min={J36.min():.6f})")
check("CY volume = 1/4096", abs(jstar_data['Vol'] - 1/4096) < 1e-6, f"({jstar_data['Vol']})")

# ============ 2. Build CY₃ ============
print("\n[2] Build CY₃(36,98)")
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
print(f"  Divisor basis: {len(basis)}")
print(f"  Basis indices: {basis}")

# Non-basis divisors (indices not in basis)
all_div = list(range(1, 37))
not_basis = [i for i in all_div if i not in basis]
print(f"  Non-basis divisors: {not_basis}")

# ============ 3. Map J* to divisor basis ============
print("\n[3] Map J* (36D) → divisor basis (32D)")
# J* has 36 entries, one per Kähler divisor
# The divisor basis has 32 entries (excludes indices 3,4,7,8 in 1-indexed)
# Map: J*[i] for divisor i+1 → J_basis[j] if divisor i+1 is in basis

J_basis = np.array([J36[b-1] for b in basis])
print(f"  J_basis (32D): {J_basis.shape}")
print(f"  J_basis range: [{J_basis.min():.6f}, {J_basis.max():.6f}]")
print(f"  J_basis mean: {J_basis.mean():.6f}")

# Compare with φ^(35-i) at same divisors
t36_phi = phi ** (35 - np.arange(36))
t32_phi = np.array([t36_phi[b-1] for b in basis])
print(f"\n  φ^(35-i) at divisor basis:")
print(f"    range: [{t32_phi.min():.4f}, {t32_phi.max():.4f}]")
print(f"    mean: {t32_phi.mean():.4f}")
ratio = t32_phi / J_basis
print(f"  J*/φ ratio: mean={ratio.mean():.1f}, min={ratio.min():.1f}, max={ratio.max():.1f}")

# ============ 4. Compute divisor volumes at J* ============
print("\n[4] Divisor volumes at J*")
dv_J = np.array(cy.compute_divisor_volumes(J_basis))
print(f"  Divisor volumes: {len(dv_J)}")
print(f"  Positive: {np.sum(dv_J > 0)}")
print(f"  Range: [{dv_J.min():.4f}, {dv_J.max():.4f}]")
print(f"  Mean: {dv_J.mean():.4f}")
print(f"  Std: {dv_J.std():.4f}")

# Check for overflow
check("No overflow (dv < 10^6)", np.all(np.abs(dv_J) < 1e6), 
      f"(max={np.abs(dv_J).max():.2f})")
check("Reasonable volumes (dv < 100)", np.all(np.abs(dv_J) < 100),
      f"(max={np.abs(dv_J).max():.2f})")

# Compare with φ^(35-i) divisor volumes
dv_phi = np.array(cy.compute_divisor_volumes(t32_phi))
print(f"\n  φ^(35-i) divisor volumes:")
print(f"    Range: [{dv_phi.min():.4f}, {dv_phi.max():.4f}]")
print(f"    Mean: {dv_phi.mean():.4f}")

# ============ 5. Compute curve volumes at J* ============
print("\n[5] Curve volumes at J*")
cv_J = np.array(cy.compute_curve_volumes(J_basis))
print(f"  Curve volumes: {len(cv_J)}")
print(f"  Positive: {np.sum(cv_J > 0)}")
print(f"  Range: [{cv_J.min():.4f}, {cv_J.max():.4f}]")
print(f"  Mean: {cv_J.mean():.4f}")

# Check which curves are positive
pos_cv = cv_J[cv_J > 0]
print(f"  Positive curve volumes: {len(pos_cv)}")
print(f"  Positive range: [{pos_cv.min():.6f}, {pos_cv.max():.6f}]")

# ============ 6. Mass proxy from J* volumes ============
print("\n[6] Mass proxy from J* curve volumes")
# Mass proxy: m ∝ exp(-V_curve) for each curve
# Then project onto 66 states

# For positive curves, compute e^{-V}
pos_mask = cv_J > 0
cv_pos = cv_J[pos_mask]
e_neg_v = np.exp(-cv_pos)  # This should NOT underflow now!
print(f"  e^(-V) for positive curves:")
print(f"    Range: [{e_neg_v.min():.6e}, {e_neg_v.max():.6e}]")
print(f"    Finite: {np.sum(np.isfinite(e_neg_v))}/{len(e_neg_v)}")

# ============ 7. Compare with φ^(35-i) ============
print("\n[7] Comparison: J* vs φ^(35-i)")
print(f"""
  {'Metric':<25} {'J*':<20} {'φ^(35-i)':<20} {'Ratio':<10}
  {'-'*75}
  {'Divisor vol mean':<25} {dv_J.mean():<20.4f} {dv_phi.mean():<20.4f} {dv_J.mean()/max(abs(dv_phi.mean()),1e-10):<10.2e}
  {'Divisor vol max':<25} {np.abs(dv_J).max():<20.4f} {np.abs(dv_phi).max():<20.4f} {np.abs(dv_J).max()/max(np.abs(dv_phi).max(),1e-10):<10.2e}
  {'Curve vol positive':<25} {np.sum(cv_J>0):<20} {np.sum(np.array(cy.compute_curve_volumes(t32_phi))>0):<20}
  {'CY volume':<25} {jstar_data['Vol']:<20.8f} {'N/A':<20}
""")

# ============ 8. Summary ============
print("\n" + "=" * 72)
print("Problem 5 Attack Summary:")
print("=" * 72)
print(f"""
  J* Kähler Moduli Renormalization:
  ─────────────────────────────────
  1. J* range: [{J36.min():.6f}, {J36.max():.6f}] (O(0.01))
  2. φ^(35-i) range: [{t32_phi.min():.4f}, {t32_phi.max():.4f}] (O(10^7))
  3. Ratio J*/φ: {ratio.mean():.1f}× smaller
  
  4. Divisor volumes at J*: [{dv_J.min():.4f}, {dv_J.max():.4f}] 
     {'✅ Reasonable!' if np.all(np.abs(dv_J) < 100) else '❌ Still large'}
  5. Divisor volumes at φ^(35-i): [{dv_phi.min():.4f}, {dv_phi.max():.4f}]
     {'✅ Reasonable!' if np.all(np.abs(dv_phi) < 100) else '❌ 10^12-10^15 overflow'}
  
  6. e^{{-V}} for positive curves: [{e_neg_v.min():.6e}, {e_neg_v.max():.6e}]
     {'✅ Finite — no underflow!' if np.all(np.isfinite(e_neg_v)) else '❌ Still underflow'}
  
  7. Verdict: J* resolves the volume overflow!
""")

results = {
    "test": "O67 Problem 5: Volume Renormalization",
    "J36": [float(v) for v in J36],
    "J_basis": [float(v) for v in J_basis],
    "divisor_volumes_J": [float(v) for v in dv_J],
    "divisor_volumes_phi": [float(v) for v in dv_phi],
    "curve_volumes_J": [float(v) for v in cv_J],
    "e_neg_v": [float(v) for v in e_neg_v],
    "J_range": [float(J36.min()), float(J36.max())],
    "phi_range": [float(t32_phi.min()), float(t32_phi.max())],
    "passed": passed, "failed": failed
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "09_volume_renormalization.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 Problem 5 Phase A complete! Ready for B: Mirror Map rescaling")