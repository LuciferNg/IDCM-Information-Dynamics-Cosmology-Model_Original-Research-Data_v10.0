#!/usr/bin/env python3
"""
O59 re-examination: Clean vs Contaminated data
Based on O137 findings about d_tensor contamination
"""
import os, json, math, numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
O53_POLY = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2

# Load clean geometric Y from true kappa * J*
with open(os.path.join(O53_POLY, "cy36_98_intersection_full.json")) as f:
    K = np.array(json.load(f)["kappa"])
with open(os.path.join(O53_POLY, "Jstar_36D.json")) as f:
    J0 = np.array(json.load(f)["Jstar_36D"])

Y_clean = np.einsum("ijk,k->ij", K, J0)
Y_clean = (Y_clean + Y_clean.T) / 2
ev_clean = np.sort(np.linalg.eigvalsh(Y_clean))
non_zero = ev_clean[abs(ev_clean) > 1e-10]

# Load contaminated d_tensor_final
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v = np.array([phi ** (-k/12) for k in range(12)])
Y_dirty = np.einsum("ijk,k->ij", d12, v)
Y_dirty = (Y_dirty + Y_dirty.T) / 2
ev_dirty = np.sort(np.linalg.eigvalsh(Y_dirty))

print("=" * 72)
print("O59 CLOSURE RE-EXAMINATION: Clean vs Contaminated")
print("=" * 72)

print("\n[1] EIGENVALUE SPECTRUM COMPARISON")
print("\n  Clean Y (kappa*J*) 36x36 spectrum (non-zero):")
print(f"  Positive: {non_zero[non_zero > 0]}")
print(f"  Negative: {non_zero[non_zero < 0]}")
print(f"  lambda_max = {ev_clean[-1]:.6f}")
print(f"  lambda_min = {ev_clean[0]:.6f}")
if len(non_zero) > 1:
    ratio = abs(non_zero[-1]) / max(np.mean(np.abs(non_zero[:-1])), 1e-12)
    print(f"  max/mean ratio = {ratio:.1f}")

print(f"\n  Contaminated d_tensor 12x12 spectrum:")
print(f"  {ev_dirty}")
print(f"  lambda_max = {ev_dirty[-1]:.6f}")
if len(ev_dirty) > 1:
    ratio_dirty = abs(ev_dirty[-1]) / max(np.mean(np.abs(ev_dirty[:-1])), 1e-12)
    print(f"  1+11 ratio = {ratio_dirty:.1f}")

print("\n[2] CHECK: Clean Y Block 0 (12x12) 1+11 structure")
b0 = Y_clean[0:12, 0:12]
ev_b0 = np.sort(np.linalg.eigvalsh(b0))
print(f"  Block 0 lambda_max = {ev_b0[-1]:.6f}")
if len(ev_b0) > 1:
    ratio_b0 = abs(ev_b0[-1]) / max(np.mean(np.abs(ev_b0[:-1])), 1e-12)
    print(f"  Block 0 1+11 ratio = {ratio_b0:.1f}")

b1 = Y_clean[12:24, 12:24]
ev_b1 = np.sort(np.linalg.eigvalsh(b1))
print(f"  Block 1 lambda_max = {ev_b1[-1]:.6f}")
if len(ev_b1) > 1:
    ratio_b1 = abs(ev_b1[-1]) / max(np.mean(np.abs(ev_b1[:-1])), 1e-12)
    print(f"  Block 1 1+11 ratio = {ratio_b1:.1f}")

b2 = Y_clean[24:36, 24:36]
ev_b2 = np.sort(np.linalg.eigvalsh(b2))
print(f"  Block 2 lambda_max = {ev_b2[-1]:.6f}")
if len(ev_b2) > 1:
    ratio_b2 = abs(ev_b2[-1]) / max(np.mean(np.abs(ev_b2[:-1])), 1e-12)
    print(f"  Block 2 1+11 ratio = {ratio_b2:.1f}")

print("\n[3] TRACE COMPARISON")
print(f"  tr(Y_clean 36x36) = {np.trace(Y_clean):.6f}")
print(f"  tr(Y_dirty 12x12) = {np.trace(Y_dirty):.6f}")
print(f"  tr(Y_dirty)/66 = {np.trace(Y_dirty)/66:.6f} (contaminated by penalty!)")
print(f"  tr(Y_clean)/66 = {np.trace(Y_clean)/66:.6f} (clean)")

print("\n[4] 66 = Lambda^2(12) WITH CLEAN DATA")
# The clean Y is 36x36, not 12x12
# To get a 12x12 Yukawa, we need to project
# Using the 3x12 block structure
print("  Clean Y is 36x36 with 3 generations of 12D blocks")
print("  The 12D Yukawa from d_tensor is NOT the same as kappa*J*")
print("  d_tensor is a derived quantity, contaminated by optimization")

print("\n[5] IMPACT ON O59 CLAIMS")
print("""
  Claim 1: 66 = Lambda^2(12) = (6,6)+(10,3bar) = 36+30
    STATUS: NEEDS RE-EXAMINATION
    - Used contaminated d_tensor_final
    - Clean Y (kappa*J*) is 36x36, not 12x12
    - The 12D d_tensor was optimized with tr(Y)->66 penalty

  Claim 2: 1+11 = Cartan(1) + Rank(11)
    STATUS: PARTIALLY VALID
    - Clean Y Block 0 has ratio ~9.8 (similar to claimed)
    - But Block 1 (1.2) and Block 2 (2.4) don't have 1+11
    - The "1" might not be Higgs but just the largest eigenvalue

  Claim 3: 33+3 = K_tree + N_gen = 3 generations
    STATUS: NEEDS RECONCILIATION
    - O137 found 44 = 28+9+5+2, not 44 = 33+3+8
    - 33 = K_tree is not in O137's 44 decomposition
    - 9 = N_gen^2 = 3^2 from phi=9 (generation mixing)
    - 3 generations from phi=9, not from 33+3

  Claim 4: 29/66 = L7/(2K_tree) correction
    STATUS: NEEDS RE-EXAMINATION
    - lambda_max = 52-29/66 was from contaminated d_tensor
    - Clean Y Block 0 lambda_max = 3.697 (not 51.56!)
    - The 12D Yukawa is different from the 36D Yukawa

  Claim 5: lambda_max = 52-29/66 -> v_geom = 246.82 GeV
    STATUS: CONTAMINATED
    - The 12D Yukawa from d_tensor was pulled toward 66
    - v_geom = 246.82 GeV came from contaminated lambda_max
    - Need clean verification with un-contaminated data
""")

print("=" * 72)
print("O59 RE-EXAMINATION COMPLETE")
print("=" * 72)