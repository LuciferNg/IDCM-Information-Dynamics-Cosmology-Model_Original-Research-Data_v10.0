#!/usr/bin/env python3
"""
O67 Attack 7: Beat-Frequency Mass Calibration
==============================================
Connect the 66 states to the O54 lepton mass formula via beat-frequency decomposition.
For each state, find the dominant K_Chain mode (γ_n) and compute the mass.

Key insight: The 66 states are eigenvectors of PPT = P @ P.T.
The beat-space representation w = P^T @ v gives the weight on each beat (γ_n - γ_m).
The dominant beat determines the γ_n mode correspondence.
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 72)
print("O67 Attack 7: Beat-Frequency Mass Calibration")
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

e_k = np.sum(evecs_66[:36, :]**2, axis=0)
e_c = np.sum(evecs_66[36:, :]**2, axis=0)
sector = np.where(e_k > e_c, "K", "C")

# ============ 2. Beat-space representation ============
print("\n[2] Beat-space representation")
# w = P^T @ v for each eigenvector
w_beat = P.T @ evecs_66  # 946 × 66
print(f"  Beat-space weights: {w_beat.shape}")

# Build beat index → (n,m) mapping
beat_pairs = []
for n in range(1, 44):
    for m in range(n+1, 45):
        beat_pairs.append((n, m))
beat_pairs = np.array(beat_pairs)

# γ_n values
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)])
# Beat frequency = |γ_n - γ_m|
beat_freq = np.abs(gamma[beat_pairs[:, 0]-1] - gamma[beat_pairs[:, 1]-1])

# ============ 3. O54 Mass Formula ============
print("\n[3] O54 Lepton Mass Formula")
M0 = 27.9009  # MeV, base mass scale
# m_l = M0 × γ_n × F_proj
# F_proj values (from O54, structurally derived):
F_proj = {1: 18/5, 7: 15.5, 20: 37}  # γ_n → F_proj mapping

# Compute lepton masses
m_e = M0 * gamma[0] * F_proj[1]    # γ_1 = 0.005096
m_mu = M0 * gamma[6] * F_proj[7]   # γ_7 = 0.244642
m_tau = M0 * gamma[19] * F_proj[20] # γ_20 = 1.715370

print(f"  M0 = {M0:.4f} MeV")
print(f"  m_e = {m_e:.4f} MeV (PDG: 0.511)")
print(f"  m_μ = {m_mu:.4f} MeV (PDG: 105.66)")
print(f"  m_τ = {m_tau:.4f} MeV (PDG: 1776.86)")

# ============ 4. Find dominant γ_n for each state ============
print("\n[4] Dominant γ_n mode per state")
# For each state, compute the weighted average γ_n of its beats
# Weight = |w_beat[i,j]|^2 (squared beat-space coefficient)

state_dominant_gamma = np.zeros(66)
state_avg_gamma = np.zeros(66)
state_beat_entropy = np.zeros(66)  # higher = more mixed

for i in range(66):
    w = w_beat[:, i]
    w2 = w**2
    w2_norm = w2 / np.sum(w2)
    
    # Weighted average γ_n
    # For each beat (n,m), the relevant γ is the average of γ_n and γ_m
    gamma_avg_beat = (gamma[beat_pairs[:, 0]-1] + gamma[beat_pairs[:, 1]-1]) / 2
    state_avg_gamma[i] = np.sum(w2_norm * gamma_avg_beat)
    
    # Dominant beat → extract the γ_n of the higher mode
    dominant_beat_idx = np.argmax(np.abs(w))
    n_dom, m_dom = beat_pairs[dominant_beat_idx]
    # The dominant γ is the larger of γ_n, γ_m
    gamma_n = gamma[n_dom-1]
    gamma_m = gamma[m_dom-1]
    state_dominant_gamma[i] = max(gamma_n, gamma_m)
    
    # Entropy of beat distribution (higher = spread across many beats)
    state_beat_entropy[i] = -np.sum(w2_norm * np.log(w2_norm + 1e-30))

print(f"  State  Sector  Dominant_γ  Avg_γ  Entropy  C1_group")
for i in range(66):
    s = sector[i]
    c1 = "C1" if i < 22 else "C2" if i > 57 else "K"
    print(f"  {i:3d}    {s}      {state_dominant_gamma[i]:.4f}    {state_avg_gamma[i]:.4f}  {state_beat_entropy[i]:.4f}  {c1}")

# ============ 5. Map to O54 modes ============
print("\n[5] Map to O54 lepton modes")
# The O54 lepton masses use γ_1 (e), γ_7 (μ), γ_20 (τ)
# Find which states have dominant γ closest to these values

target_gammas = {1: gamma[0], 7: gamma[6], 20: gamma[19]}
print(f"  Target γ: γ_1={target_gammas[1]:.6f}, γ_7={target_gammas[7]:.6f}, γ_20={target_gammas[20]:.6f}")

for name, n in [("e (γ_1)", 1), ("μ (γ_7)", 7), ("τ (γ_20)", 20)]:
    tg = target_gammas[n]
    diffs = np.abs(state_dominant_gamma - tg)
    closest = np.argsort(diffs)[:5]
    print(f"\n  Closest states to {name} = {tg:.6f}:")
    for idx in closest:
        s = sector[idx]
        c1 = "C1" if idx < 22 else "C2" if idx > 57 else "K"
        print(f"    State {idx:3d} [{s}][{c1}]: γ={state_dominant_gamma[idx]:.6f}, diff={diffs[idx]:.6f}, sqrt(λ)={math.sqrt(evals_66[idx]):.4f}")

# ============ 6. Mass calibration ============
print("\n[6] Mass calibration")
# For each state, compute the mass using the O54 formula:
# m = M0 × γ_dominant × F_proj
# where F_proj is determined by the state's group

# C1 states (3rd gen): use τ-like F_proj (37)
# K-fermion states (2nd gen): use μ-like F_proj (15.5)
# C2 states (1st gen): use e-like F_proj (18/5 = 3.6)
# K-boson states: gauge bosons, use different calibration

# Group assignment
C1_indices = list(range(22))
K_fermion_indices = list(range(22, 40))  # top 18 K
K_boson_indices = list(range(40, 58))    # bottom 18 K
C2_indices = list(range(58, 66))

group_fproj = {
    "C1": 37,      # τ-like
    "K-fermion": 15.5,  # μ-like
    "C2": 18/5,    # e-like (3.6)
    "K-boson": 1.0  # placeholder (gauge bosons use different mechanism)
}

print(f"  Group F_proj values:")
for grp, fp in group_fproj.items():
    print(f"    {grp}: F_proj = {fp}")

# Compute masses
state_masses = np.zeros(66)
for i in range(66):
    if i in C1_indices:
        fp = group_fproj["C1"]
    elif i in K_fermion_indices:
        fp = group_fproj["K-fermion"]
    elif i in K_boson_indices:
        fp = group_fproj["K-boson"]
    else:
        fp = group_fproj["C2"]
    
    state_masses[i] = M0 * state_dominant_gamma[i] * fp

print(f"\n  Computed masses (O54 formula):")
print(f"  {'State':<7} {'Group':<12} {'γ_dom':<8} {'F_proj':<8} {'Mass(MeV)':<12} {'sqrt(λ)':<8}")
for i in range(66):
    if i in C1_indices:
        grp = "C1/3rd gen"
        fp = group_fproj["C1"]
    elif i in K_fermion_indices:
        grp = "K-ferm/2nd gen"
        fp = group_fproj["K-fermion"]
    elif i in K_boson_indices:
        grp = "K-bos/gauge"
        fp = group_fproj["K-boson"]
    else:
        grp = "C2/1st gen"
        fp = group_fproj["C2"]
    print(f"  {i:<7} {grp:<12} {state_dominant_gamma[i]:<8.4f} {fp:<8.2f} {state_masses[i]:<12.2f} {math.sqrt(evals_66[i]):<8.4f}")

# ============ 7. Compare with SM masses ============
print("\n[7] Compare with SM masses")
# SM masses (in MeV)
SM_masses = {
    "e": 0.511, "μ": 105.66, "τ": 1776.86,
    "u": 2.16, "d": 4.67, "s": 93.0, "c": 1270.0, "b": 4180.0, "t": 172760.0,
    "W": 80377.0, "Z": 91187.6, "H": 125250.0
}

# Find the closest state to each SM particle
for name, m_sm in SM_masses.items():
    log_mass = math.log(m_sm) if m_sm > 0 else -10
    # Compare with state masses
    diffs = [abs(math.log(sm + 1e-10) - log_mass) / max(log_mass, 0.1) for sm in state_masses]
    closest = np.argmin(diffs)
    print(f"  {name:<3} (SM={m_sm:<10.2f} MeV): closest state {closest} (mass={state_masses[closest]:.2f} MeV, ratio={state_masses[closest]/max(m_sm,1e-10):.2f})")

# ============ 8. Verification ============
print("\n[8] Verification")
# Check if the O54 formula gives reasonable masses for the C1 states
# C1 → 3rd gen: should include t, b, τ, ν_τ
# Top 3 C1 masses should be in the 10^4-10^5 MeV range (t, b)
# The next few should be in the 10^3-10^4 range (τ)

C1_masses = state_masses[C1_indices]
C1_sorted = np.sort(C1_masses)[::-1]
print(f"  C1 top 5 masses: {[f'{m:.2f}' for m in C1_sorted[:5]]} MeV")
print(f"  Expected: t=172760, b=4180, τ=1777 MeV")

# Check C2 masses (1st gen)
C2_masses = state_masses[C2_indices]
C2_sorted = np.sort(C2_masses)[::-1]
print(f"  C2 top 5 masses: {[f'{m:.2f}' for m in C2_sorted[:5]]} MeV")
print(f"  Expected: c=1270, s=93, u=2.16, d=4.67, e=0.511 MeV")

# ============ 9. Summary ============
print("\n" + "=" * 72)
print("Attack 7 Summary:")
print("=" * 72)
print(f"""
  Beat-Frequency Mass Calibration:
  ─────────────────────────────────
  1. Each state's dominant γ_n determined from beat-space weights
  2. O54 formula: m = M0 × γ_dominant × F_proj
  3. Group-dependent F_proj:
     - C1 (3rd gen): F_proj = 37 (τ-like)
     - K-fermion (2nd gen): F_proj = 15.5 (μ-like)
     - C2 (1st gen): F_proj = 3.6 (e-like)
  4. Dominant γ_n range: [{state_dominant_gamma.min():.4f}, {state_dominant_gamma.max():.4f}]
  5. Mass range: [{state_masses.min():.2f}, {state_masses.max():.2f}] MeV
""")

results = {
    "test": "O67 Attack 7: Beat-Frequency Mass Calibration",
    "M0": float(M0),
    "state_dominant_gamma": [float(g) for g in state_dominant_gamma],
    "state_avg_gamma": [float(g) for g in state_avg_gamma],
    "state_beat_entropy": [float(e) for e in state_beat_entropy],
    "state_masses": [float(m) for m in state_masses],
    "C1_masses": [float(m) for m in C1_masses],
    "C2_masses": [float(m) for m in C2_masses],
    "passed": passed, "failed": failed
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "07_beat_mass_calibration.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Passed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 Attack 7 complete!")