#!/usr/bin/env python3
"""
O2 Step 6: Gain Restoration — 反卷積傳遞函數還原
===================================================
Concept: F₆-F₈ 的「消失」是網絡傳輸衰減（Topological Damping）
+ 平滑濾波（Low-pass Filtering）的必然結果。

Method: 以 F₅=150μK 為 0dB reference，對每個 BFS 層級
計算補償因子（Gain Factor），還原被衰減的高階 Fibonacci 振幅。

Reference: F₄/F₅ = Unity Gain (0 dB)
           F₆ = 240 μK, F₇ = 390 μK, F₈ = 631 μK
           
Caution: Gain boosting amplifies noise floor too.
         Use Wiener-like regularization: only boost nodes
         with statistical significance.
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
FWHM_DEG = 3.0  # 3° 平滑 (最佳尺度)
sigma_rad = np.radians(FWHM_DEG) / (2 * np.sqrt(2 * np.log(2)))

# Fibonacci theoretical levels (μK)
F_THEORY = {'F₅': 150, 'F₄': 93, 'F₃': 57, 'F₂': 35, 'F₁': 22, 'F₆': 240, 'F₇': 390, 'F₈': 631}

# 6-level ladder model (from Step 4 fit)
LADDER_6LEVEL = {0: 150, 1: 93, 2: 57, 3: 35, 4: 35, 5: 22, 6: 22, 7: 22, 8: 22}

print("=" * 70)
print("O2 STEP 6: GAIN RESTORATION (反卷積傳遞函數還原)")
print("=" * 70)

# 1. Read SMICA at 3° smoothing
print(f"\n[1/6] Reading SMICA ({FWHM_DEG}° smoothing)...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
T = m_s * 1e6

# 2. Read nodes and sample
print(f"\n[2/6] Sampling 60 nodes...")
nodes_radec = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes_radec[:,0]*u.deg, dec=nodes_radec[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T_nodes = T[pix]

coloring = np.loadtxt(COLORING, usecols=[0, 3])
color = coloring[:, 1]  # 0=hot, 1=cold

# 3. Build adjacency + BFS distances
print(f"\n[3/6] Building BFS distance graph...")
vec_nodes = hp.ang2vec(l_deg, b_deg, lonlat=True)
cos_dists = np.dot(vec_nodes, vec_nodes.T)
cos_dists = np.clip(cos_dists, -1, 1)
ang_dists = np.degrees(np.arccos(cos_dists))

THRESHOLD = 28.0
adj = {i: set() for i in range(60)}
for i in range(60):
    for j in range(i+1, 60):
        if ang_dists[i, j] < THRESHOLD:
            adj[i].add(j)
            adj[j].add(i)

# BFS from node 0 (cold spot)
bfs_dist = {0: 0}
q = deque([0])
while q:
    v = q.popleft()
    for nb in adj[v]:
        if nb not in bfs_dist:
            bfs_dist[nb] = bfs_dist[v] + 1
            q.append(nb)

max_dist = max(bfs_dist.values())
print(f"  BFS distances: {sorted(set(bfs_dist.values()))}")
print(f"  Diameter: {max_dist}")

# 4. Compute per-BFS-layer statistics
print(f"\n[4/6] Computing per-layer observed vs theoretical amplitudes...")

# Sky noise estimate (for regularization)
sky_noise = np.std(T)  # μK
print(f"  Sky noise (std): {sky_noise:.1f} μK")

print(f"\n  {'Layer':>5s}  {'Nodes':>5s}  {'Observed Mean':>14s}  {'Theory (6-lvl)':>14s}  {'Gain Factor':>11s}  {'S/N':>5s}  {'Status':>8s}")
print(f"  {'-'*70}")

gain_factors = {}
for d in range(max_dist + 1):
    nodes_at_d = [i for i in range(60) if bfs_dist[i] == d]
    if not nodes_at_d:
        continue
    T_d = T_nodes[nodes_at_d]
    obs_mean = np.mean(np.abs(T_d))
    theory = LADDER_6LEVEL[d]
    
    # Gain factor = theory / observed (with regularization)
    if obs_mean > sky_noise * 0.5:  # Only compute if above noise floor
        gain = theory / obs_mean
    else:
        gain = 1.0  # No boost for noise-dominated layers
    
    # S/N ratio
    sn = obs_mean / sky_noise
    
    # Status
    if obs_mean < sky_noise:
        status = 'NOISE'
    elif gain > 1.5:
        status = 'BOOST'
    elif gain > 1.1:
        status = 'SLIGHT'
    else:
        status = 'UNITY'
    
    gain_factors[d] = gain
    print(f"  d={d:1d}  {len(nodes_at_d):5d}  {obs_mean:14.1f} μK  {theory:14.0f} μK  {gain:11.3f}x  {sn:5.2f}  {status:>8s}")

# 5. Apply gain compensation to all 60 nodes
print(f"\n[5/6] Applying gain compensation to all 60 nodes...")

T_compensated = np.zeros(60)
T_original = T_nodes.copy()
noise_amp = np.zeros(60)  # Amplified noise estimate

for i in range(60):
    d = bfs_dist[i]
    gain = gain_factors.get(d, 1.0)
    T_compensated[i] = T_nodes[i] * gain
    noise_amp[i] = sky_noise * gain  # Noise gets amplified too!

print(f"\n  {'Node':>4s}  {'Color':>6s}  {'BFS d':>5s}  {'Original':>9s}  {'Gain':>6s}  {'Compensated':>12s}  {'Noise':>7s}  {'S/N':>6s}")
print(f"  {'-'*65}")

# Sort by compensated absolute value
sorted_idx = np.argsort(np.abs(T_compensated))[::-1]
for rank in range(60):
    i = sorted_idx[rank]
    d = bfs_dist[i]
    gain = gain_factors.get(d, 1.0)
    c = 'HOT' if color[i] == 0 else 'COLD'
    sn_comp = abs(T_compensated[i]) / noise_amp[i]
    print(f"  {i:4d}  {c:>6s}  {d:5d}  {T_original[i]:+9.1f}  {gain:6.2f}x  {T_compensated[i]:+12.1f} μK  {noise_amp[i]:6.1f}  {sn_comp:6.2f}")

# 6. Check: do any compensated nodes reach F₆/F₇/F₈ levels?
print(f"\n[6/6] Checking Fibonacci level reach after compensation...")

print(f"\n  {'Level':>6s}  {'Value':>6s}  {'Nodes >= Level':>18s}  {'Best Node':>12s}  {'Status':>10s}")
print(f"  {'-'*60}")

for name, val in [('F₅', 150), ('F₆', 240), ('F₇', 390), ('F₈', 631)]:
    above = np.abs(T_compensated) >= val
    n_above = np.sum(above)
    if n_above > 0:
        best = np.argmax(np.abs(T_compensated) * above)
        best_val = T_compensated[best]
        c = 'HOT' if color[best] == 0 else 'COLD'
        print(f"  {name:>6s}  {val:6d}  {n_above:4d} / 60 nodes        {best_val:+7.1f} μK ({c})  {'✅' if n_above>0 else '❌':>10s}")
    else:
        best = np.argmax(np.abs(T_compensated))
        print(f"  {name:>6s}  {val:6d}  {'0 / 60 nodes':>18s}  {T_compensated[best]:+7.1f} μK max  {'❌':>10s}")

# Also check: original vs compensated distribution
print(f"\n{'='*70}")
print(f"GAIN RESTORATION SUMMARY")
print(f"{'='*70}")

print(f"\n  Original hot node mean:    {np.mean(np.abs(T_original[color==0])):.1f} μK")
print(f"  Compensated hot node mean: {np.mean(np.abs(T_compensated[color==0])):.1f} μK")
print(f"  Boost factor:              {np.mean(np.abs(T_compensated[color==0])) / np.mean(np.abs(T_original[color==0])):.2f}x")

print(f"\n  Original cold node mean:    {np.mean(np.abs(T_original[color==1])):.1f} μK")
print(f"  Compensated cold node mean: {np.mean(np.abs(T_compensated[color==1])):.1f} μK")

# Top 5 hot nodes after compensation
print(f"\n  Top 5 hot nodes (compensated):")
comp_hot = T_compensated[color==0]
comp_hot_idx = np.where(color==0)[0]
comp_hot_sorted = np.argsort(comp_hot)[::-1]
for rank in range(min(5, len(comp_hot_sorted))):
    i = comp_hot_idx[comp_hot_sorted[rank]]
    d = bfs_dist[i]
    print(f"    #{rank+1}: node {i:2d} (BFS d={d})  {T_original[i]:+.1f} → {T_compensated[i]:+.1f} μK")

# Save results
print(f"\n  Saving results...")
with open(os.path.join(OUTDIR, 'gain_restoration.txt'), 'w') as f:
    f.write(f"# Gain restoration results\n")
    f.write(f"# Smoothing: {FWHM_DEG}° FWHM\n")
    f.write(f"# Reference: F₅=150μK (0dB)\n")
    f.write(f"# Ladder model: 6-level\n\n")
    f.write(f"# Per-layer gain factors:\n")
    for d in range(max_dist + 1):
        gain = gain_factors.get(d, 1.0)
        f.write(f"d={d} gain={gain:.3f}\n")
    f.write(f"\n# Node data: idx, color, bfs_d, T_original, T_compensated, noise_amplified\n")
    for i in range(60):
        d = bfs_dist[i]
        c = 0 if color[i]==0 else 1
        f.write(f"{i} {c} {d} {T_original[i]:.1f} {T_compensated[i]:.1f} {noise_amp[i]:.1f}\n")

print(f"✅ Saved: data/gain_restoration.txt")
print(f"\n{'='*70}")
print(f"O2 STEP 6 COMPLETE")
print(f"{'='*70}")