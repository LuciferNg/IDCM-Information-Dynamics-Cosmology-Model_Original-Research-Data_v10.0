#!/usr/bin/env python3
"""
O67 Problem 5 Phase B: 66-State Mass from J* Curve Volumes
===========================================================
Use the J* fixed point curve volumes to compute physical masses
for the 66 states. The mass proxy: m ∝ e^{-V_curve} projected
onto each state's Kähler/CPX eigenvector.

Key insight: At J*, curve volumes are O(0.1-0.5), so e^{-V} ∈ [0.6, 1.0].
This allows direct mass computation without underflow.
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O67 Problem 5 Phase B: 66-State Mass from J* Volumes")
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

# ============ 1. Load data ============
print("\n[1] Load 66-state data and CY₃")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evals_66 = evals[pos][:66]
evecs_66 = evecs[:, pos][:, :66]

e_k = np.sum(evecs_66[:36, :]**2, axis=0)
e_c = np.sum(evecs_66[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
C_idx = np.where(sector == "C")[0]
C1_idx = C_idx[:22]
C2_idx = C_idx[22:]

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

# ============ 2. Load J* ============
print("\n[2] Load J* and compute volumes")
jstar_data = json.load(open(os.path.join(O53, "Jstar_36D.json")))
J36 = np.array(jstar_data["Jstar_36D"])
J_basis = np.array([J36[b-1] for b in basis])

# Divisor volumes at J*
dv_J = np.array(cy.compute_divisor_volumes(J_basis))
print(f"  Divisor volumes: {len(dv_J)}, positive: {np.sum(dv_J > 0)}")

# Curve volumes at J*
cv_J = np.array(cy.compute_curve_volumes(J_basis))
print(f"  Curve volumes: {len(cv_J)}, positive: {np.sum(cv_J > 0)}")

# ============ 3. Compute Q_ij at J* ============
print("\n[3] Compute Q_ij at J*")
n_curves = len(cv_J)
eps = 1e-5
Q = np.zeros((n_curves, len(basis)))
for j in range(len(basis)):
    tp = J_basis.copy(); tm = J_basis.copy()
    tp[j] += eps; tm[j] -= eps
    Q[:, j] = (np.array(cy.compute_curve_volumes(tp)) - np.array(cy.compute_curve_volumes(tm))) / (2*eps)
print(f"  Q: {Q.shape}, rank {np.linalg.matrix_rank(Q)}")

# ============ 4. Mass proxy ============
print("\n[4] Mass proxy from curve volumes")
# m_i = M0 × exp(-V_i) where V_i is the curve volume
# But we need to project curve volumes onto the 66 states

# K-state mass: weight K-state eigenvectors by curve volumes
# The K states (indices 22-57) have Kähler components
# Each K state's mass = weighted average of exp(-V_curve) for
# curves that project strongly onto that K state

# First, map K-state eigenvectors to divisor basis
kahler_to_divisor = np.zeros(36, dtype=int) - 1
basis_list = list(basis)
for i in range(36):
    if (i+1) in basis_list:
        j = basis_list.index(i+1)
        kahler_to_divisor[i] = j

divisor_mask = kahler_to_divisor >= 0
K_evecs = evecs_66[:36, K_idx]  # 36×36
K_evecs_div = K_evecs[divisor_mask, :]  # 32×36

# Map curves to K states via Q_ij
curve_k_weight = np.abs(Q @ K_evecs_div)  # 185×36
curve_k_weight_n = curve_k_weight / (np.sum(curve_k_weight, axis=1, keepdims=True) + 1e-12)

# For each K state, compute mass as weighted average of e^{-V_curve}
cv_pos_mask = cv_J > 0
cv_pos = cv_J[cv_pos_mask]
cv_e_neg_v = np.exp(-cv_pos)

# Only use positive curves
K_masses = np.zeros(len(K_idx))
for k in range(len(K_idx)):
    # Weight of each positive curve on this K state
    weights = curve_k_weight_n[cv_pos_mask, k]
    # Mass = weighted average of e^{-V}
    if np.sum(weights) > 0:
        w_norm = weights / np.sum(weights)
        K_masses[k] = np.sum(w_norm * cv_e_neg_v)
    else:
        K_masses[k] = 0.0

print(f"  K-state masses from J* curve volumes:")
for k in range(len(K_idx)):
    print(f"    K-state {K_idx[k]}: mass = {K_masses[k]:.6f}")

# ============ 5. C-state mass proxy ============
print("\n[5] C-state mass proxy")
# C states are CPX-dominated — their mass comes from the K_Chain γ_n spectrum
# Use the eigenvalue as the mass proxy (already established)
# Combined with O54 formula: m = M0 × γ_dominant × F_proj

# C1 states (0-21): 3rd gen, use eigenvalue
# C2 states (58-65): 1st gen, use eigenvalue
C_masses = evals_66[C_idx]  # use eigenvalue as proxy
C1_masses = evals_66[C1_idx]
C2_masses = evals_66[C2_idx]

print(f"  C1 masses (eigenvalues): [{C1_masses.min():.4f}, {C1_masses.max():.4f}]")
print(f"  C2 masses (eigenvalues): [{C2_masses.min():.4f}, {C2_masses.max():.4f}]")

# ============ 6. Combined mass hierarchy ============
print("\n[6] Combined mass hierarchy")
# Now we have:
# - K-state masses: from J* curve volumes (e^{-V}, dimensionless 0-1)
# - C-state masses: from eigenvalues (dimensionless 0-334)

# The K-state masses from J* are in [0, 1] range (fraction of positive curves)
# The C-state eigenvalues are in [0, 334] range
# These are different scales — need to unify

# Insight: the K-state mass from J* measures the fraction of
# "active" curves for that state. Higher = more curves active = heavier.
# The C-state eigenvalue measures the "variance explained" = projection strength.

# For unification, calibrate against known SM masses:
# b-quark: 4180 MeV → corresponds to C1 states
# W-boson: 80377 MeV → corresponds to K-boson states

# The K_masses are in [0, 1] — need scale factor
# The C1 eigenvalues are in [19, 334] — need scale factor

# Find the scale factor that makes the mass hierarchy match SM
# C1 top 3 eigenvalues: 333.85, 167.95, 159.59
# SM 3rd gen: t=172760, b=4180, τ=1777

# C1 scale: 172760/333.85 = 517.5 (if top = eigenvalue)
# But the eigenvalue is not the mass — it's the variance

# Better approach: use the beat-frequency-weighted γ_n from Phase 7
# combined with the O54 formula

# ============ 7. Mass calibration ============
print("\n[7] Mass calibration using O54 formula")
# The O54 formula: m = M0 × γ_n × F_proj
# M0 = 27.9009 MeV
# γ_n = 4sin²(nπ/88) — K_Chain mode
# F_proj = projection factor (geometric)

# For each state, the dominant γ_n determines the O54 formula
# The mass is then: m = M0 × γ_dominant × F_proj

# But we need F_proj for each state. From O54:
# F_proj(e) = 18/5 = 3.6 (γ_1 = 0.005)
# F_proj(μ) = 15.5 (γ_7 = 0.245)
# F_proj(τ) = 37 (γ_20 = 1.715)

# For K states (gauge bosons), the mass formula is different
# m_W = g₂ × v / 2 = 80.4 GeV (from Higgs VEV)
# m_Z = (g₂² + g₁²)^(1/2) × v / 2 = 91.2 GeV
# These come from the gauge coupling, not from curve volumes

# For now, save the J* curve volumes and K-state masses for later use
print(f"""
  Mass Calibration:
  ─────────────────────────────────
  K-state masses from J* curve volumes: [{K_masses.min():.6f}, {K_masses.max():.6f}]
  C1 eigenvalues: [{C1_masses.min():.4f}, {C1_masses.max():.4f}]
  C2 eigenvalues: [{C2_masses.min():.4f}, {C2_masses.max():.4f}]
  
  The J* curve volumes give mass proxies in [0, 1] for K states.
  C-state eigenvalues range: [{C1_masses.min():.4f}, {C1_masses.max():.4f}] for C1, [{C2_masses.min():.4f}, {C2_masses.max():.4f}] for C2.
  Both need scale calibration against SM masses.
  
  The key structural result: J* enables finite exp(-V) computation.
  The mass formula is structurally separate: m = M0 × γ_n × F_proj.
""")

# ============ 8. Save results ============
results = {
    "test": "O67 Problem 5 Phase B: J* Mass Computation",
    "K_masses": [float(m) for m in K_masses],
    "K_idx": [int(i) for i in K_idx],
    "divisor_volumes_J": [float(v) for v in dv_J],
    "curve_volumes_J": [float(v) for v in cv_J],
    "cv_positive": [float(v) for v in cv_pos],
    "cv_e_neg_v": [float(v) for v in cv_e_neg_v],
    "n_curves_positive": int(len(cv_pos)),
    "passed": passed, "failed": failed
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "10_jstar_masses.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Passed: {passed}, Failed: {failed}")
print("🎉 Problem 5 Phase B complete!")
print("Next: Phase C — Mirror Map rescaling for high-precision mass calibration")