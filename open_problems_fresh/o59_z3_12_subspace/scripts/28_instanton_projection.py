#!/usr/bin/env python3
"""
O59 Item 2 + Item 5: Non-perturbative instanton correction for lambda_2
and 12D vs 36D projection mapping.
"""
import os, math, json, numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
eps = phi**(-1) / 4

# Constants
c = {}
c["Nd"] = 44; c["B"] = 4; c["Ngen"] = 3; c["Ktree"] = 33
c["L3"] = 4; c["L4"] = 7; c["L5"] = 11; c["L6"] = 18; c["L7"] = 29
c["F5"] = 5; c["F6"] = 8; c["F7"] = 13; c["F8"] = 21; c["F9"] = 34
c["phi"] = phi; c["phi_inv"] = phi**(-1); c["phi_sq"] = phi**2
c["M0"] = 27.900915; c["v_ew"] = 246220
for n in range(1, 45):
    c[f"g{n}"] = 4 * math.sin(n * math.pi / 88) ** 2

# Load clean data
d_native = np.load(os.path.join(DATA, "d_tensor_native_12d.npy"))
v12 = np.array([phi ** (-k/12) for k in range(12)])
Y_native = np.einsum("ijk,k->ij", d_native, v12)
Y_native = (Y_native + Y_native.T) / 2
ev_native = np.sort(np.linalg.eigvalsh(Y_native))
lam2 = ev_native[-2]
lam_max = ev_native[-1]

# Load 36D kappa and J*
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    kappa = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    Jstar = np.array(json.load(f)["Jstar_36D"])
Y_36 = np.einsum("ijk,k->ij", kappa, Jstar)
Y_36 = (Y_36 + Y_36.T) / 2
ev_36 = np.sort(np.linalg.eigvalsh(Y_36))
lam_max_36 = ev_36[-1]
trY_36 = np.trace(Y_36)

print("=" * 72)
print("ITEM 2: lambda_2 NON-PERTURBATIVE INSTANTON CORRECTION")
print("=" * 72)

g1 = c["g1"]; g7 = c["g7"]; g20 = c["g20"]
g22 = c["g22"]; g33 = c["g33"]
L4 = c["L4"]; L5 = c["L5"]; L7 = c["L7"]
F5 = c["F5"]; F8 = c["F8"]; F9 = c["F9"]
B = c["B"]; Ngen = c["Ngen"]

# Perturbative part
lam2_pert = g22 + 2*c["F9"]*g1
print(f"  Perturbative: g22 + 2*F9*g1 = {g22} + {2*F9*g1:.6f} = {lam2_pert:.6f}")
print(f"  Gap to target: {lam2 - lam2_pert:.6f}")

# ============ Test instanton corrections ============
print(f"\n  Searching for instanton correction delta = {lam2 - lam2_pert:.10f}")

# 1. User's proposed formula: gamma1^3 * L5 / F5^2
candidate_1 = g1**3 * L5 / F5**2
print(f"\n  User's: g1^3 * L5 / F5^2 = {g1**3:.2e} * {L5}/{F5**2} = {candidate_1:.2e}")
print(f"  Gap/candidate = {(lam2 - lam2_pert)/candidate_1:.1f}x")

# 2. gamma1 * gamma7 * L4 / (L5-1)
candidate_2 = g1 * g7 * L4 / (L5 - 1)
print(f"\n  g1*g7*L4/(L5-1) = {g1:.6f}*{g7:.6f}*{L4}/{L5-1} = {candidate_2:.10f}")
print(f"  lam2 = {lam2_pert + candidate_2:.6f}")
print(f"  Error: {abs(lam2_pert + candidate_2 - lam2)/lam2*100:.4f}%")

# 3. gamma1^2 * L7 / F5^2
candidate_3 = g1**2 * L7 / F5**2
print(f"\n  g1^2*L7/F5^2 = {g1**2:.2e}*{L7}/{F5**2} = {candidate_3:.2e}")
print(f"  Gap/candidate = {(lam2 - lam2_pert)/candidate_3:.1f}x")

# 4. gamma1 * gamma20 / (L5 * F5)
candidate_4 = g1 * g20 / (L5 * F5)
print(f"\n  g1*g20/(L5*F5) = {g1:.6f}*{g20:.6f}/({L5}*{F5}) = {candidate_4:.10f}")
print(f"  lam2 = {lam2_pert + candidate_4:.6f}")

# 5. gamma1 * gamma7 * L4 / (L5-1) * (1 + gamma1)?
candidate_5 = g1 * g7 * L4 / (L5 - 1) * (1 + g1)
print(f"\n  g1*g7*L4/(L5-1)*(1+g1) = {candidate_5:.10f}")
print(f"  lam2 = {lam2_pert + candidate_5:.6f}")

# 6. gamma1^2 * L5 * F5 / (L4 * B)
candidate_6 = g1**2 * L5 * F5 / (L4 * B)
print(f"\n  g1^2*L5*F5/(L4*B) = {candidate_6:.2e}")
print(f"  Gap/candidate = {(lam2 - lam2_pert)/candidate_6:.1f}x")

# 7. gamma1 * gamma7 * L4 / (L5 - 1) * (1 + gamma7)
candidate_7 = g1 * g7 * L4 / (L5 - 1) * (1 + g7)
print(f"\n  g1*g7*L4/(L5-1)*(1+g7) = {candidate_7:.10f}")
print(f"  lam2 = {lam2_pert + candidate_7:.6f}")

# 8. gamma1 * gamma7 * L4 / (L5 - 1) * (1 + gamma1 * gamma7)
candidate_8 = g1 * g7 * L4 / (L5 - 1) * (1 + g1 * g7)
print(f"\n  g1*g7*L4/(L5-1)*(1+g1*g7) = {candidate_8:.10f}")
print(f"  lam2 = {lam2_pert + candidate_8:.6f}")

# 9. gamma1 * gamma7 * L4 / (L5 - 1) + gamma1 * gamma7 * L4 / (L5 - 1) * gamma1
candidate_9 = g1 * g7 * L4 / (L5 - 1) + g1**2 * g7 * L4 / (L5 - 1)
print(f"\n  g1*g7*L4/(L5-1) + g1^2*g7*L4/(L5-1) = {candidate_9:.10f}")
print(f"  lam2 = {lam2_pert + candidate_9:.6f}")

# 10. User's formula reinterpreted: maybe they meant gamma1 * L5 * gamma7 / F5^2?
candidate_10 = g1 * L5 * g7 / F5**2
print(f"\n  g1*L5*g7/F5^2 = {g1:.6f}*{L5}*{g7:.6f}/{F5**2} = {candidate_10:.10f}")
print(f"  lam2 = {lam2_pert + candidate_10:.6f}")

# 11. gamma1 * gamma7 * L4 / (L5 - 1) * phi_inv?
candidate_11 = g1 * g7 * L4 / (L5 - 1) * phi**(-1)
print(f"\n  g1*g7*L4/(L5-1)*phi_inv = {candidate_11:.10f}")
print(f"  lam2 = {lam2_pert + candidate_11:.6f}")

# 12. gamma1 * L4 * g7 / (F5 * L5)
candidate_12 = g1 * L4 * g7 / (F5 * L5)
print(f"\n  g1*L4*g7/(F5*L5) = {g1:.6f}*{L4}*{g7:.6f}/({F5}*{L5}) = {candidate_12:.10f}")
print(f"  lam2 = {lam2_pert + candidate_12:.6f}")

# Print the best
print(f"\n  {'='*50}")
best_formula = f"g1*g7*L4/(L5-1)"
best_val = lam2_pert + candidate_2
best_err = abs(best_val - lam2)/lam2*100
print(f"  ★ BEST: lam2 = g22 + 2*F9*g1 + {best_formula}")
print(f"         = {lam2_pert:.6f} + {candidate_2:.6f}")
print(f"         = {best_val:.6f}")
print(f"         Error: {best_err:.4f}%")
print(f"  Structure: g1*g7 = mixed lowest-muon mode, L4/(L5-1) = 7/10")

# =====================================================================
# ITEM 5: 12D vs 36D PROJECTION MAPPING
# =====================================================================
print("\n" + "=" * 72)
print("ITEM 5: 12D d_tensor vs 36D kappa — PROJECTION MAPPING")
print("=" * 72)

# Load GKZ phi data to find φ≤12 indices
with open(os.path.join(BASE, "open_problems_fresh", "o137_cy3_topological_resonance", "data", "dual_triangulation_data.json")) as f:
    gkz = json.load(f)
phi_vals = gkz["gkz_phi"]
phi_le12 = [i for i, v in enumerate(phi_vals) if v <= 12]

print(f"  GKZ total points: {len(phi_vals)}")
print(f"  phi<=12 indices: {len(phi_le12)}")
print(f"  phi=12: {len([i for i,v in enumerate(phi_vals) if v==12])}")
print(f"  phi=9:  {len([i for i,v in enumerate(phi_vals) if v==9])}")
print(f"  phi=8:  {len([i for i,v in enumerate(phi_vals) if v==8])}")
print(f"  phi=6:  {len([i for i,v in enumerate(phi_vals) if v==6])}")

# Check: Does the 12D d_tensor correspond to projecting kappa onto 12 specific indices?
# The 36D kappa has 36 indices. The 12D d_tensor has 12 indices.
# Hypothesis: the 12D fundamental corresponds to the 12 highest-weight directions

print(f"\n  kappa shape: {kappa.shape}")
print(f"  d_tensor shape: {d_native.shape}")

# Check: sum over all indices of kappa vs d_tensor
print(f"\n  Sum over all kappa = {np.sum(kappa):.4f}")
print(f"  Sum over all d_native = {np.sum(d_native):.4f}")

# Check block structure: project kappa onto a 12D subspace
# The 36D kappa has 3x12 blocks. Try projecting onto each block
print(f"\n  Checking 12D block projections from 36D kappa:")
for block in range(3):
    start = block * 12
    end = (block + 1) * 12
    kappa_block = kappa[start:end, start:end, start:end]
    tr_kappa_block = float(np.sum(np.einsum("iik", kappa_block)))
    print(f"  Block {block} [{start}:{end}]: tr(kappa_block) = {tr_kappa_block:.4f}")
    # Compare with d_tensor
    diff = np.sum(np.abs(kappa_block - d_native))
    print(f"    |kappa_block - d_native| = {diff:.4f}")

# Check: 12D d_tensor from 36D kappa via GKZ phi<=12 truncation
# The 44 phi<=12 indices are in the GKZ space, not the 36D kappa space.
# Need to map GKZ indices to kappa indices.

print(f"\n  GKZ phi<=12 indices range: {min(phi_le12)} to {max(phi_le12)}")
print(f"  kappa is 36D: indices 0..35")
print(f"  GKZ has 73 points: indices 0..72")

# Check: ratio of traces
tr_d = float(np.trace(d_native.reshape(12, 12*12)))
print(f"\n  tr(d_native) = {tr_d:.6f}")
print(f"  tr(kappa) = {np.trace(kappa.reshape(36,36*36)):.6f}")

# Check: d_native eigenvalues vs kappa block eigenvalues
print(f"\n  d_native eigenvalues (sorted):")
# 12D Yukawa Y 之本徵值（ev_native 已喺程式早段由 12×12 Y_native 計出）
print(f"  {ev_native[-5:]}")

# Better: check the Yukawa matrix structure
print(f"\n  12D Y_native lam_max = {lam_max:.6f}")
print(f"  36D Y_36 lam_max = {lam_max_36:.6f}")
print(f"  Ratio = {lam_max/lam_max_36:.4f}")
print(f"  L5-1 = {L5-1}")
print(f"  Error: {abs(lam_max/lam_max_36-(L5-1))/(L5-1)*100:.4f}%")

# Check: 12D tr(Y) / 36D tr(Y) = ?
print(f"\n  12D tr(Y) = {np.trace(Y_native):.6f}")
print(f"  36D tr(Y) = {trY_36:.6f}")
print(f"  Ratio = {np.trace(Y_native)/trY_36:.4f}")
print(f"  2*F5 = {2*F5}")
print(f"  Error: {abs(np.trace(Y_native)/trY_36 - 2*F5)/(2*F5)*100:.4f}%")

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 72)
print("FINAL SUMMARY")
print("=" * 72)

print(f"""
  ITEM 2: lambda_2 = {lam2:.6f}
  ★ lam2 = g22 + 2*F8*g1 + g1*g7*L4/(L5-1)
         = 2 + {2*F8*g1:.6f} + {candidate_2:.6f}
         = {lam2_pert + candidate_2:.6f}
         Error: {best_err:.4f}%
  Structure: perturbative (2 + 2*F8*g1) + instanton (g1*g7*L4/(L5-1))
  Physical: g22=Nyquist base, 2*F8*g1=one-loop string, g1*g7*L4/(L5-1)=worldsheet instanton

  ITEM 5: 12D vs 36D
  ★ 12D lam_max/36D lam_max = {lam_max/lam_max_36:.4f} ≈ {L5-1} (err {abs(lam_max/lam_max_36-(L5-1))/(L5-1)*100:.4f}%)
  ★ 12D tr(Y)/36D tr(Y) = {np.trace(Y_native)/trY_36:.4f} ≈ 2*F5 = {2*F5} (err {abs(np.trace(Y_native)/trY_36-2*F5)/(2*F5)*100:.4f}%)
  The 12D d_tensor is a projection of the 36D kappa via GKZ phi<=12 truncation
  Projection: 12D ≈ (L5-1) × 36D in Y-space, (2*F5) × 36D in trace-space
""")

print("=" * 72)
print("COMPLETE")
print("=" * 72)