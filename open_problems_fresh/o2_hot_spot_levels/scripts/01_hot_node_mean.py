#!/usr/bin/env python3
"""
O2 Step 1: Hot node mean temperature
======================================
Read 30 hot-colored nodes from anchored_coloring.txt,
sample SMICA 5° smoothed map, compute mean temperature.

Output: mean, std, individual node temps, comparison to F₆/F₇/F₈
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import sys, os

# Paths
SMICA = '/tmp/smica2.fits'
NODES = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
COLORING = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/data'

os.makedirs(OUTDIR, exist_ok=True)

# Smoothing parameters
FWHM_DEG = 5.0
sigma_rad = np.radians(FWHM_DEG) / (2 * np.sqrt(2 * np.log(2)))

print("=" * 60)
print("O2 STEP 1: HOT NODE MEAN TEMPERATURE")
print("=" * 60)

# 1. Read SMICA
print("\n[1/7] Reading SMICA...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
print(f"  NSIDE = {nside}, pixels = {len(m):,}")
print(f"  Raw map std = {np.std(m)*1e6:.1f} μK")

# 2. Smooth
print(f"\n[2/7] Smoothing to {FWHM_DEG}° FWHM (σ = {np.degrees(sigma_rad):.3f}°)...")
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
smoothed_std = np.std(m_s) * 1e6
print(f"  Smoothed map std = {smoothed_std:.1f} μK")

# 3. Read nodes
print("\n[3/7] Reading 60 nodes (ICRS RA, Dec)...")
nodes_radec = np.loadtxt(NODES)
ra_deg, dec_deg = nodes_radec[:, 0], nodes_radec[:, 1]
print(f"  {len(ra_deg)} nodes loaded")

# 4. Convert to Galactic
print("\n[4/7] Converting ICRS → Galactic...")
sc = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg

# 5. Sample SMICA at node positions
print("\n[5/7] Sampling SMICA at node positions...")
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)
T = m_s[pix] * 1e6  # μK

# 6. Read coloring
print("\n[6/7] Reading anchored coloring (cold=1, hot=0)...")
coloring = np.loadtxt(COLORING, usecols=[0, 3])
node_idx = coloring[:, 0].astype(int)
color = coloring[:, 1]
assert np.all(node_idx == np.arange(60)), "Node order mismatch!"

# 7. Analysis
print("\n[7/7] Analyzing hot nodes...")

# Hot nodes (color=0)
hot_mask = (color == 0)
hot_indices = np.where(hot_mask)[0]
hot_T = T[hot_indices]
hot_l = l_deg[hot_indices]
hot_b = b_deg[hot_indices]

# Cold nodes (color=1) for comparison
cold_mask = (color == 1)
cold_indices = np.where(cold_mask)[0]
cold_T = T[cold_indices]

print(f"\n{'='*60}")
print(f"HOT NODES (n={len(hot_T)}, color=0)")
print(f"{'='*60}")
print(f"  Mean:     {np.mean(hot_T):+.1f} ± {np.std(hot_T):.1f} μK")
print(f"  Median:   {np.median(hot_T):+.1f} μK")
print(f"  Min:      {np.min(hot_T):+.1f} μK")
print(f"  Max:      {np.max(hot_T):+.1f} μK")
print(f"  # positive:  {np.sum(hot_T > 0)} / {len(hot_T)}")
print(f"  # negative:  {np.sum(hot_T < 0)} / {len(hot_T)}")

if np.mean(hot_T) > 0:
    print(f"\n  ✅ Hot nodes are indeed warm on average (mean = {np.mean(hot_T):+.1f} μK)")
else:
    print(f"\n  ❌ Hot nodes are NOT warm on average")

print(f"\n{'='*60}")
print(f"COLD NODES (n={len(cold_T)}, color=1) — comparison")
print(f"{'='*60}")
print(f"  Mean:     {np.mean(cold_T):+.1f} ± {np.std(cold_T):.1f} μK")
print(f"  Median:   {np.median(cold_T):+.1f} μK")
print(f"  Cold spot (node 0): {T[0]:+.1f} μK")

print(f"\n{'='*60}")
print(f"HOT-COLD SEPARATION")
print(f"{'='*60}")
gap = np.mean(hot_T) - np.mean(cold_T)
print(f"  Hot − Cold mean: {gap:+.1f} μK")
print(f"  Effect size (Cohen's d): {gap / np.sqrt((np.std(hot_T)**2 + np.std(cold_T)**2)/2):.3f}")

print(f"\n{'='*60}")
print(f"FIBONACCI LEVEL COMPARISON (hot node mean)")
print(f"{'='*60}")
F_levels = {'F₅ (cold spot)': 150.0, 'F₆': 240.0, 'F₇': 390.0, 'F₈': 631.0}
for name, val in F_levels.items():
    ratio = np.mean(hot_T) / val
    print(f"  {name:16s} = {val:4.0f} μK  →  mean/ratio = {ratio:.3f}")

# Distribution of individual hot nodes
print(f"\n{'='*60}")
print(f"INDIVIDUAL HOT NODE TEMPERATURES (sorted)")
print(f"{'='*60}")
sorted_idx = np.argsort(hot_T)[::-1]  # descending
for rank, si in enumerate(sorted_idx):
    i = hot_indices[si]
    print(f"  #{rank+1:2d}  node {i:2d}  (l={hot_l[si]:7.2f}°, b={hot_b[si]:7.2f}°)  {hot_T[si]:+7.1f} μK")

# Also list the top 10 hottest nodes overall (regardless of color)
print(f"\n{'='*60}")
print(f"TOP 10 HOTTEST NODES (all 60)")
print(f"{'='*60}")
all_sorted = np.argsort(T)[::-1]
for rank in range(10):
    i = all_sorted[rank]
    c = 'HOT' if color[i] == 0 else 'COLD'
    print(f"  #{rank+1:2d}  node {i:2d}  ({c})  (l={l_deg[i]:7.2f}°, b={b_deg[i]:7.2f}°)  {T[i]:+7.1f} μK")

# Bottom 10 coldest
print(f"\n{'='*60}")
print(f"BOTTOM 10 COLDEST NODES (all 60)")
print(f"{'='*60}")
for rank in range(10):
    i = all_sorted[-(rank+1)]
    c = 'HOT' if color[i] == 0 else 'COLD'
    print(f"  #{rank+1:2d}  node {i:2d}  ({c})  (l={l_deg[i]:7.2f}°, b={b_deg[i]:7.2f}°)  {T[i]:+7.1f} μK")

# Save results
print(f"\n{'='*60}")
out = np.column_stack([hot_indices, hot_l, hot_b, hot_T])
np.savetxt(os.path.join(OUTDIR, 'hot_node_temps.txt'), out,
           fmt='%d %.4f %.4f %.1f',
           header='idx l_deg b_deg T_muK')
print(f"✅ Saved: data/hot_node_temps.txt")

out_all = np.column_stack([np.arange(60), l_deg, b_deg, T, color])
np.savetxt(os.path.join(OUTDIR, 'all_node_temps_smoothed.txt'), out_all,
           fmt='%d %.4f %.4f %.1f %d',
           header='idx l_deg b_deg T_muK color(0=hot,1=cold)')
print(f"✅ Saved: data/all_node_temps_smoothed.txt")

print(f"\n{'='*60}")
print(f"O2 STEP 1 COMPLETE")
print(f"{'='*60}")