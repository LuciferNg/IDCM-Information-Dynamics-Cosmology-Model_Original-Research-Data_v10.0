#!/usr/bin/env python3
"""
O2 Step 8: Multiscale Analysis — 0.5°~15° 多尺度掃描
=====================================================
Find the optimal smoothing scale for each Fibonacci level.
F₅ (cold spot) best at 3°.
F₆/F₇/F₈ may appear at finer scales.

For each scale: cold spot T, all-sky max, node statistics,
sign-aligned stacking.

Also try: raw (un-smoothed) + bandpass filters.
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

# Fibonacci levels
F_LEVELS = {'F₅': 150, 'F₆': 240, 'F₇': 390, 'F₈': 631}

print("=" * 70)
print("O2 STEP 8: MULTISCALE ANALYSIS (0.5°–15° + raw + bandpass)")
print("=" * 70)

# 1. Read SMICA
print(f"\n[1/4] Reading SMICA...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
print(f"  NSIDE = {nside}")

# 2. Read nodes
print(f"\n[2/4] Reading 60 nodes...")
nodes_radec = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes_radec[:,0]*u.deg, dec=nodes_radec[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg
pix = hp.ang2pix(nside, l_deg, b_deg, lonlat=True)

coloring = np.loadtxt(COLORING, usecols=[0, 3])
color = coloring[:, 1]
sign = np.where(color == 0, 1, -1)

# 3. Build BFS graph
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

# 4. Multiscale scan
print(f"\n[3/4] Multiscale scanning...")

# Smoothing scales to test
scales = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 15.0]
# 0.0 = raw (un-smoothed)
# Also try bandpass

print(f"  {'Scale':>6s}  {'Map σ':>6s}  {'Cold T':>8s}  {'Hot μ':>8s}  {'Cold μ':>8s}  {'Gap':>8s}  {'Stack S':>8s}  {'Mask Max':>8s}  {'F₅ hit':>8s}  {'F₆ hit':>8s}")
print(f"  {'-'*95}")

results = []
for FWHM in scales:
    if FWHM == 0.0:
        # Raw (un-smoothed)
        m_s = hp.remove_dipole(m.copy())
        label = 'raw'
    else:
        sigma_rad = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
        label = f'{FWHM:.1f}°'
    
    T_map = m_s * 1e6
    map_std = np.std(T_map)
    T_nodes = T_map[pix]
    
    # Cold spot
    pix_cs = hp.ang2pix(nside, 209.0, -57.0, lonlat=True)
    T_cold = T_map[pix_cs]
    
    # Hot node mean
    hot_mean = np.mean(T_nodes[color == 0])
    cold_mean = np.mean(T_nodes[color == 1])
    gap = hot_mean - cold_mean
    
    # Sign-aligned stack
    S = np.mean(T_nodes * sign)
    
    # All-sky max (masked |b|>=25)
    l_all, b_all = hp.pix2ang(nside, np.arange(len(T_map)), lonlat=True)
    mask = np.abs(b_all) >= 25
    T_masked = T_map.copy()
    T_masked[~mask] = -np.inf
    max_masked = np.nanmax(T_masked)
    
    # F₅ hit? F₆ hit?
    f5_hit = "✅" if max_masked >= 150 else "❌"
    f6_hit = "✅" if max_masked >= 240 else "❌"
    
    print(f"  {label:>6s}  {map_std:6.1f}  {T_cold:8.1f}  {hot_mean:8.1f}  {cold_mean:8.1f}  {gap:8.1f}  {S:8.1f}  {max_masked:8.1f}  {f5_hit:>8s}  {f6_hit:>8s}")
    
    results.append({
        'scale': FWHM, 'label': label,
        'map_std': map_std, 'T_cold': T_cold,
        'hot_mean': hot_mean, 'cold_mean': cold_mean,
        'gap': gap, 'S': S, 'max_masked': max_masked,
        'f5_hit': f5_hit, 'f6_hit': f6_hit
    })

# 4b. Bandpass filters
print(f"\n  Bandpass filters:")
for lmin, lmax in [(2, 30), (2, 60), (2, 100), (20, 100), (30, 200), (50, 300)]:
    # Use alm transform
    alm = hp.map2alm(m, lmax=lmax)
    # Filter
    alm_filt = hp.almxfl(alm, np.zeros(lmax+1))
    # Actually, proper bandpass: set l < lmin and l > lmax to 0
    ls = np.arange(lmax+1)
    filt = np.where((ls >= lmin) & (ls <= lmax), 1.0, 0.0)
    alm_filt = hp.almxfl(alm, filt)
    m_bp = hp.alm2map(alm_filt, nside=nside)
    m_bp = hp.remove_dipole(m_bp)
    T_bp = m_bp * 1e6
    map_std = np.std(T_bp)
    T_nodes_bp = T_bp[pix]
    
    pix_cs = hp.ang2pix(nside, 209.0, -57.0, lonlat=True)
    T_cold = T_bp[pix_cs]
    hot_mean = np.mean(T_nodes_bp[color == 0])
    S = np.mean(T_nodes_bp * sign)
    
    # Masked max
    l_all, b_all = hp.pix2ang(nside, np.arange(len(T_bp)), lonlat=True)
    mask = np.abs(b_all) >= 25
    T_m = T_bp.copy()
    T_m[~mask] = -np.inf
    max_masked = np.nanmax(T_m)
    f5 = "✅" if max_masked >= 150 else "❌"
    f6 = "✅" if max_masked >= 240 else "❌"
    
    print(f"  ℓ∈[{lmin:3d},{lmax:3d}]  {map_std:6.1f}  {T_cold:8.1f}  {hot_mean:8.1f}  {S:8.1f}  {max_masked:8.1f}  {f5:>8s}  {f6:>8s}")

# 5. Best scale analysis
print(f"\n[4/4] Best scale analysis")

# Find which scale gives the best cold spot
best_cold = max(results, key=lambda r: abs(r['T_cold']))
print(f"  Best cold spot: {best_cold['label']} = {best_cold['T_cold']:.1f} μK")

# Best gap
best_gap = max(results, key=lambda r: r['gap'])
print(f"  Best hot-cold gap: {best_gap['label']} = {best_gap['gap']:.1f} μK")

# Best stack S
best_S = max(results, key=lambda r: r['S'])
print(f"  Best sign-aligned stack: {best_S['label']} = {best_S['S']:.1f} μK")

# Best masked max
best_max = max(results, key=lambda r: r['max_masked'])
print(f"  Best masked max: {best_max['label']} = {best_max['max_masked']:.1f} μK")

# Check if any scale reaches F₆
f6_scales = [r for r in results if r['f6_hit'] == '✅']
print(f"  Scales reaching F₆=240μK: {len(f6_scales)}")
for r in f6_scales:
    print(f"    {r['label']}: {r['max_masked']:.1f} μK")

# Save results
print(f"\n  Saving results...")
with open(os.path.join(OUTDIR, 'multiscale_scan.txt'), 'w') as f:
    f.write(f"# Multiscale scan results\n")
    f.write(f"# scale(map_std) cold_T hot_mean cold_mean gap stack_S masked_max\n")
    for r in results:
        f.write(f"{r['scale']:.1f} {r['map_std']:.1f} {r['T_cold']:.1f} {r['hot_mean']:.1f} {r['cold_mean']:.1f} {r['gap']:.1f} {r['S']:.1f} {r['max_masked']:.1f}\n")

print(f"✅ Saved: data/multiscale_scan.txt")
print(f"\n{'='*70}")
print(f"O2 STEP 8 COMPLETE")
print(f"{'='*70}")