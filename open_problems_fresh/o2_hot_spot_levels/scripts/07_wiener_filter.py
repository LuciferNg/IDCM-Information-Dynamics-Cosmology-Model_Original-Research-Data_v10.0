#!/usr/bin/env python3
"""
O2 Step 7: Wiener Filter Restoration — S/N-adaptive Matched Filter
====================================================================
Concept: Uses the BFS ladder model + anchored coloring as a strong
signal prior. Wiener weights = A(d)² / (A(d)² + σ²_noise).

Three tests:
1. Sign-aligned Wiener-weighted stacking (z vs random coloring)
2. Per-layer Wiener restoration
3. Wiener residual analysis (signal - model after optimal filtering)

Reference: F₅=150μK (0dB), 6-level ladder model
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from collections import deque
import sys, os

SMICA = '/tmp/smica2.fits'
NODES = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
COLORING = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/data'
os.makedirs(OUTDIR, exist_ok=True)

# === Parameters ===
FWHM_DEG = 3.0  # Optimal scale from Step 6
sigma_rad = np.radians(FWHM_DEG) / (2 * np.sqrt(2 * np.log(2)))

# 6-level ladder model (from Step 4 fit)
LADDER = {0: 150, 1: 93, 2: 57, 3: 35, 4: 35, 5: 22, 6: 22, 7: 22, 8: 22}

print("=" * 70)
print("O2 STEP 7: WIENER FILTER — S/N-adaptive Matched Filter")
print("=" * 70)

# 1. Read SMICA
print(f"\n[1/7] Reading SMICA ({FWHM_DEG}° smoothing)...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
T = m_s * 1e6
sky_noise = np.std(T)
print(f"  Sky noise (σ): {sky_noise:.1f} μK")

# 2. Read nodes
print(f"\n[2/7] Sampling 60 nodes...")
nodes_radec = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes_radec[:,0]*u.deg, dec=nodes_radec[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_nodes = T[pix]

coloring = np.loadtxt(COLORING, usecols=[0, 3])
color = coloring[:, 1]  # 0=hot, 1=cold

# Sign: hot→+1, cold→-1
sign = np.where(color == 0, 1, -1)

# 3. Build adjacency + BFS distances
print(f"\n[3/7] Building BFS distance graph...")
vec_nodes = hp.ang2vec(l_deg, b_deg, lonlat=True)
cos_dists = np.dot(vec_nodes, vec_nodes.T)
cos_dists = np.clip(cos_dists, -1, 1)
ang_dists = np.degrees(np.arccos(cos_dists))

adj = {i: set() for i in range(60)}
for i in range(60):
    for j in range(i+1, 60):
        if ang_dists[i, j] < 28.0:
            adj[i].add(j)
            adj[j].add(i)

bfs_dist = {0: 0}
q = deque([0])
while q:
    v = q.popleft()
    for nb in adj[v]:
        if nb not in bfs_dist:
            bfs_dist[nb] = bfs_dist[v] + 1
            q.append(nb)

max_dist = max(bfs_dist.values())

# 4. Compute Wiener weights
print(f"\n[4/7] Computing Wiener weights...")
print(f"  {'Layer':>5s}  {'A(d)':>7s}  {'A²':>8s}  {'A²/(A²+σ²)':>14s}  {'Nodes':>5s}")
print(f"  {'-'*45}")

wiener_weights = np.zeros(60)
expected_signal = np.zeros(60)
for i in range(60):
    d = bfs_dist[i]
    A = LADDER[d]
    expected_signal[i] = sign[i] * A
    # Wiener weight: signal power / (signal power + noise power)
    w = A**2 / (A**2 + sky_noise**2)
    wiener_weights[i] = w

for d in range(max_dist + 1):
    nodes_at_d = [i for i in range(60) if bfs_dist[i] == d]
    if not nodes_at_d:
        continue
    A = LADDER[d]
    w = A**2 / (A**2 + sky_noise**2)
    print(f"  d={d:1d}  {A:7.0f}  {A**2:8.0f}  {w:14.4f}  {len(nodes_at_d):5d}")

# 5. Test 1: Wiener-weighted sign-aligned stacking
print(f"\n[5/7] Test 1: Wiener-weighted sign-aligned stacking")

# Observed sign-aligned value (with Wiener weights)
T_aligned = T_nodes * sign  # Positive if hot→hot, cold→cold
S_obs = np.average(T_aligned, weights=wiener_weights)
S_uniform = np.mean(T_aligned)  # Uniform weighting for comparison

print(f"  Uniform-weighted S:  {S_uniform:+.1f} μK")
print(f"  Wiener-weighted S:   {S_obs:+.1f} μK")
print(f"  Wiener weights mean: {np.mean(wiener_weights):.4f}")

# Random coloring test (5000x)
rng = np.random.default_rng(42)
n_perm = 5000
S_rand = np.zeros(n_perm)
for i in range(n_perm):
    rand_sign = rng.choice([-1, 1], size=60)
    S_rand[i] = np.average(T_nodes * rand_sign, weights=wiener_weights)

mu_rand = np.mean(S_rand)
std_rand = np.std(S_rand)
z = (S_obs - mu_rand) / std_rand
p = np.sum(S_rand >= S_obs) / n_perm

print(f"\n  Random coloring (n={n_perm}):")
print(f"    Null mean: {mu_rand:.2f} μK")
print(f"    Null std:  {std_rand:.2f} μK")
print(f"    Observed:  {S_obs:+.2f} μK")
print(f"    z-score:   {z:.2f} σ")
print(f"    p-value:   {p:.4f}")

if z > 2.0:
    print(f"  ✅ Wiener-weighted stacking: SIGNIFICANT (>{2}σ)")
elif z > 1.5:
    print(f"  🟡 Wiener-weighted stacking: marginal (>1.5σ)")
else:
    print(f"  ❌ Wiener-weighted stacking: NOT significant")

# 6. Test 2: Per-layer Wiener restoration
print(f"\n[6/7] Test 2: Per-layer Wiener restoration")

# Apply Wiener filter: T_restored = model + w * (observed - model)
# This pulls noisy observations toward the model prediction
T_restored = expected_signal + wiener_weights * (T_nodes - expected_signal)

# Residual: T_residual = T_restored - expected_signal = w * (T_obs - expected)
# If filter works, residuals should be white noise
T_residual = T_restored - expected_signal

print(f"  {'Layer':>5s}  {'Nodes':>5s}  {'Expected':>9s}  {'Observed μ':>10s}  {'Restored μ':>10s}  {'Residual μ':>10s}  {'Res std':>8s}")
print(f"  {'-'*65}")

for d in range(max_dist + 1):
    nodes_at_d = [i for i in range(60) if bfs_dist[i] == d]
    if not nodes_at_d:
        continue
    exp = LADDER[d]
    obs_mean = np.mean(T_nodes[nodes_at_d])
    obs_std = np.std(T_nodes[nodes_at_d])
    res_mean = np.mean(T_residual[nodes_at_d])
    res_std = np.std(T_residual[nodes_at_d])
    # Sign-aligned mean
    aligned_mean = np.mean(T_nodes[nodes_at_d] * sign[nodes_at_d])
    print(f"  d={d:1d}  {len(nodes_at_d):5d}  {exp:>+9.0f}  {obs_mean:>+10.1f}  {obs_std:>8.1f}  {res_mean:>+10.2f}  {res_std:>7.1f}")

# 7. Test 3: Wiener residual analysis
print(f"\n[7/7] Test 3: Wiener residual analysis")

# Residual statistics
res_std_total = np.std(T_residual)
res_mean_total = np.mean(T_residual)
print(f"  Residual total: mean = {res_mean_total:+.2f}, std = {res_std_total:.1f} μK")
print(f"  Original noise: σ = {sky_noise:.1f} μK")
print(f"  Noise reduction: {(1 - res_std_total/sky_noise)*100:.1f}%")

# Check if residuals show any remaining structure
print(f"\n  Top 5 residual nodes (largest |residual|):")
res_sorted = np.argsort(np.abs(T_residual))[::-1]
for rank in range(5):
    i = res_sorted[rank]
    d = bfs_dist[i]
    c = 'HOT' if color[i]==0 else 'COLD'
    print(f"    #{rank+1}: node {i:2d} ({c}, d={d})  obs={T_nodes[i]:+7.1f}  exp={expected_signal[i]:+7.1f}  res={T_residual[i]:+7.1f}")

# Save results
print(f"\n  Saving results...")
with open(os.path.join(OUTDIR, 'wiener_filter.txt'), 'w') as f:
    f.write(f"# Wiener filter results\n")
    f.write(f"# Smoothing: {FWHM_DEG}° FWHM\n")
    f.write(f"# Sky noise: {sky_noise:.1f} μK\n")
    f.write(f"# Wiener-weighted stacking: S={S_obs:.2f}, z={z:.2f}, p={p:.4f}\n")
    f.write(f"# Uniform stacking: S={S_uniform:.2f}\n\n")
    f.write(f"# Node data: idx, color, bfs_d, T_obs, sign, expected, wiener_w, T_restored, residual\n")
    for i in range(60):
        c = 0 if color[i]==0 else 1
        d = bfs_dist[i]
        f.write(f"{i} {c} {d} {T_nodes[i]:.1f} {sign[i]:+d} {expected_signal[i]:.1f} {wiener_weights[i]:.4f} {T_restored[i]:.1f} {T_residual[i]:.1f}\n")

print(f"✅ Saved: data/wiener_filter.txt")
print(f"\n{'='*70}")
print(f"O2 STEP 7 COMPLETE")
print(f"{'='*70}")