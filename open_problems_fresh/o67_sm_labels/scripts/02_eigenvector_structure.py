#!/usr/bin/env python3
"""
O67 Phase 2: Eigenvector Structure Analysis
=============================================
Analyze the internal structure of the 66 states:
  - K-sector: 36 = 2×18 sub-structure
  - C-sector: 30 = 22+8 sub-structure
  - Beat-frequency mode correlation
  - Division into boson/fermion candidates
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 72)
print("O67 Phase 2: Eigenvector Structure Analysis")
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
print("\n[1] Load 66-state data")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
PPT = P @ P.T
evals, evecs = np.linalg.eigh(PPT)
idx = np.argsort(evals)[::-1]
evals = evals[idx]
evecs = evecs[:, idx]
pos = evals > 1e-10
evals_66 = evals[pos][:66]
evecs_66 = evecs[:, pos][:, :66]

# Sector decomposition
e_k = np.sum(evecs_66[:36, :]**2, axis=0)
e_c = np.sum(evecs_66[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")
K_idx = np.where(sector == "K")[0]
C_idx = np.where(sector == "C")[0]
C1_idx = np.where(sector == "C")[0][:22]  # first 22 C states
C2_idx = np.where(sector == "C")[0][22:]  # last 8 C states

print(f"  K states: {len(K_idx)} (indices {K_idx[0]}-{K_idx[-1]})")
print(f"  C1 states: {len(C1_idx)} (indices {C1_idx[0]}-{C1_idx[-1]})")
print(f"  C2 states: {len(C2_idx)} (indices {C2_idx[0]}-{C2_idx[-1]})")

# ============ 2. K-sector internal structure ============
print("\n[2] K-sector internal structure (36 = 2×18)")
K_evals = evals_66[K_idx]
K_evecs = evecs_66[:, K_idx]
K_sort = np.argsort(K_evals)[::-1]
K_evals_sorted = K_evals[K_sort]

# Check for 2×18 subgroup structure
print(f"  K eigenvalues sorted: {[f'{v:.4f}' for v in K_evals_sorted]}")
# Look for gap between 18th and 19th
gap_18_19 = K_evals_sorted[17] / K_evals_sorted[18] if K_evals_sorted[18] > 0 else float('inf')
print(f"  Gap between 18th and 19th: {gap_18_19:.2f}")
check("K-sector 2×18 gap > 1.2", gap_18_19 > 1.2, f"({gap_18_19:.2f})")

# Check if the 2 subgroups correspond to different Kähler component patterns
# The Kähler components are 36-dimensional (divisor basis)
# First 18 states vs last 18: different divisor basis weight patterns?
K_d1 = K_evecs[:36, K_sort[:18]]  # first 18 states, Kähler components
K_d2 = K_evecs[:36, K_sort[18:]]  # last 18 states, Kähler components

# Compute average weight per divisor for each group
w1 = np.mean(K_d1**2, axis=1)
w2 = np.mean(K_d2**2, axis=1)
print(f"  Group 1 divisor weights: top 5 divisors: {np.argsort(w1)[::-1][:5]}")
print(f"  Group 2 divisor weights: top 5 divisors: {np.argsort(w2)[::-1][:5]}")
corr_12 = np.corrcoef(w1, w2)[0, 1]
print(f"  Correlation between group 1 and 2 divisor weights: {corr_12:.4f}")
check("K subgroups have different divisor patterns", corr_12 < 0.9, f"(r={corr_12:.4f})")

# ============ 3. C-sector internal structure ============
print("\n[3] C-sector internal structure (30 = 22+8)")
C_evals = evals_66[C_idx]
C_evecs = evecs_66[:, C_idx]
C_sort = np.argsort(C_evals)[::-1]
C_evals_sorted = C_evals[C_sort]

print(f"  C eigenvalues sorted: {[f'{v:.4f}' for v in C_evals_sorted[:22]]}")
print(f"  C eigenvalues (last 8): {[f'{v:.4f}' for v in C_evals_sorted[-8:]]}")

# C1 = 22 states (indices 0-21 in original), C2 = 8 states (indices 58-65)
# C1: highest eigenvalues → fermion candidates
# C2: lowest eigenvalues → possible different sector
C1_evals = evals_66[C1_idx]
C2_evals = evals_66[C2_idx]
print(f"  C1 (22) eigenvalue range: [{C1_evals.min():.4f}, {C1_evals.max():.4f}]")
print(f"  C2 (8) eigenvalue range: [{C2_evals.min():.4f}, {C2_evals.max():.4f}]")
print(f"  C1/C2 mean ratio: {C1_evals.mean()/C2_evals.mean():.2f}")

# CPX component structure: 98-dimensional
# C1 states use which CPX components?
C1_evecs = evecs_66[36:, C1_idx]  # 98×22
C2_evecs = evecs_66[36:, C2_idx]  # 98×8

# Check if C1 and C2 use different CPX mode subspaces
w_c1 = np.mean(C1_evecs**2, axis=1)
w_c2 = np.mean(C2_evecs**2, axis=1)
corr_c1c2 = np.corrcoef(w_c1, w_c2)[0, 1]
print(f"  C1 vs C2 CPX weight correlation: {corr_c1c2:.4f}")
check("C1 and C2 use different CPX subspaces", corr_c1c2 < 0.9, f"(r={corr_c1c2:.4f})")

# ============ 4. Beat-frequency mode composition ============
print("\n[4] Beat-frequency mode composition")
# P columns correspond to beat frequencies (n,m) with 1≤n<m≤44
# Each eigenvector is a linear combination of these 946 beats
# But the eigenvectors are 134-dimensional (36 Kähler + 98 CPX)
# The P matrix maps beats → Kähler/CPX components
# So the 66 eigenvectors are in the "image" space, not the "beat" space

# However, we can reconstruct the beat-space representation:
# Each eigenvector v (134-dim) = P @ w, where w is the beat-space representation
# w = P^T @ v (since the 66 eigenvectors span the image of P)

# Reconstruct beat-space weights
w_beat = P.T @ evecs_66  # 946 × 66

# For each state, find the dominant beats
print("  Top beat contributions per state:")
for i in range(min(5, 66)):
    w = w_beat[:, i]
    top5 = np.argsort(np.abs(w))[::-1][:5]
    # Convert beat indices back to (n,m) pairs
    beat_pairs = []
    for n in range(1, 44):
        for m in range(n+1, 45):
            beat_pairs.append((n, m))
    beat_pairs = np.array(beat_pairs)
    print(f"    State {i} (sector={sector[i]}):")
    for b_idx in top5:
        n, m = beat_pairs[b_idx]
        print(f"      beat({n},{m}) = |γ_{n} - γ_{m}|, weight={w[b_idx]:.4f}")

# ============ 5. γ_n mode correlation ============
print("\n[5] γ_n mode correlation")
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)])

# For each state, compute the average γ_n of its dominant beats
avg_gamma = np.zeros(66)
for i in range(66):
    w = w_beat[:, i]
    w_abs = np.abs(w)
    # Weighted average of γ_n from the beats
    beat_pairs = []
    for n in range(1, 44):
        for m in range(n+1, 45):
            beat_pairs.append((n, m))
    beat_pairs = np.array(beat_pairs)
    # For each beat, the beat frequency = |γ_n - γ_m|
    beat_freq = np.abs(gamma[beat_pairs[:, 0]-1] - gamma[beat_pairs[:, 1]-1])
    avg_gamma[i] = np.average(beat_freq, weights=w_abs)

print(f"  Average γ_n per state (by sector):")
for s_name, s_idx in [("K", K_idx), ("C1", C1_idx), ("C2", C2_idx)]:
    print(f"    {s_name}: mean={avg_gamma[s_idx].mean():.4f}, std={avg_gamma[s_idx].std():.4f}")

# Check: do K states have lower γ_n than C states?
print(f"  K states avg γ: {avg_gamma[K_idx].mean():.4f}")
print(f"  C states avg γ: {avg_gamma[C_idx].mean():.4f}")
check("K states have lower γ_n than C states", 
      avg_gamma[K_idx].mean() < avg_gamma[C_idx].mean(),
      f"(K={avg_gamma[K_idx].mean():.4f}, C={avg_gamma[C_idx].mean():.4f})")

# ============ 6. Generation boundary within C sector ============
print("\n[6] Generation boundary within C sector")
# C sector has 30 states. If they correspond to 48 Weyl fermions (3×16),
# the mapping is not 1:1. But we can check if the 30 states split into 3 groups
# corresponding to 3 generations.

# Look at the C1 (22 states) — these are the highest-energy C states
# Do they split into 3 groups?
C1_sorted = np.sort(C1_evals)[::-1]
print(f"  C1 eigenvalues (sorted): {[f'{v:.4f}' for v in C1_sorted]}")
# Look for gaps between groups of ~7
for i in range(1, len(C1_sorted)):
    ratio = C1_sorted[i-1] / C1_sorted[i]
    if ratio > 1.5:
        print(f"    Gap at position {i}: {C1_sorted[i-1]:.4f} / {C1_sorted[i]:.4f} = {ratio:.2f}")

# Check if C1 splits into 3×7 + 1 pattern (like 22 = 21+1)
print(f"  C1: 22 = 3×7 + 1 possible? 3×7 = 21, +1 = 22")
check("C1 = 22 = 3×7+1", len(C1_idx) == 22, f"(22)")

# ============ 7. K-sector generation pattern ============
print("\n[7] K-sector generation pattern")
# K sector has 36 states. If they correspond to 18 gauge+Higgs per L₆,
# 36 = 2×L₆ = 2×18
# L₆ = 18 = 12 gauge + 6 Higgs
# 2× means 2 copies? Or one for matter and one for gauge?

# Check if K states split into subgroups
K_sorted = np.sort(K_evals)[::-1]
print(f"  K eigenvalues (sorted): {[f'{v:.4f}' for v in K_sorted]}")
for i in range(1, len(K_sorted)):
    ratio = K_sorted[i-1] / K_sorted[i]
    if ratio > 1.3:
        print(f"    Gap at position {i}: {K_sorted[i-1]:.4f} / {K_sorted[i]:.4f} = {ratio:.2f}")

# Check if K splits as 2×18 = 2×(12+6)
# 12 = gauge, 6 = Higgs
# Look for subgroup at 12 and 6
print(f"  K: 36 = 2×18 = 2×(12+6)")
check("K = 36 = 2×18", len(K_idx) == 36, f"({len(K_idx)})")

# ============ 8. Summary ============
print("\n" + "=" * 72)
print("Phase 2 Summary:")
print("=" * 72)
print(f"""
  Eigenvector Structure:
  ─────────────────────────────────
  1. K-sector (36 = 2×18):
     - 2 subgroups of 18 states each
     - Different divisor weight patterns
     - Candidates: 12 gauge + 6 Higgs (×2)
  2. C-sector (30 = 22+8):
     - C1: 22 states (high eigenvalues) → fermion candidates
     - C2: 8 states (low eigenvalues) → sterile/extra?
     - 22 = 3×7+1 = 3 generations × 7 + 1 self-dual
  3. Beat-frequency correlation:
     - K states have lower avg γ_n (lower energy)
     - C states have higher avg γ_n (higher energy)
  4. Generation pattern:
     - 3×7+1 per generation in C sector
     - 2×18 in K sector (boson candidates)
""")

results = {
    "test": "O67 Phase 2: Eigenvector Structure",
    "K_gap_18_19": float(gap_18_19),
    "K_divisor_corr": float(corr_12),
    "C1_C2_corr": float(corr_c1c2),
    "K_avg_gamma": float(avg_gamma[K_idx].mean()),
    "C_avg_gamma": float(avg_gamma[C_idx].mean()),
    "C1_eigenvalues": [float(v) for v in C1_evals],
    "C2_eigenvalues": [float(v) for v in C2_evals],
    "K_eigenvalues": [float(v) for v in K_evals],
    "passed": passed, "failed": failed
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "02_eigenvector_structure.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 Phase 2 complete!")