#!/usr/bin/env python3
"""
O2 Step 2: Antipode scan
=========================
Cold spot = (l,b) = (209°, -57°)
Antipode = (29°, +57°)
Scan 5° radius around antipode for maximum positive temperature.

Also scans the full 5° FWHM disk around the antipode for mean T.
"""

import numpy as np
import healpy as hp
import sys, os

SMICA = '/tmp/smica2.fits'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/data'

os.makedirs(OUTDIR, exist_ok=True)

# Parameters
COLD_SPOT = (209.0, -57.0)  # (l, b) Galactic
ANTIPODE = (29.0, 57.0)     # antipode
SEARCH_RADIUS_DEG = 5.0
FWHM_DEG = 5.0

sigma_rad = np.radians(FWHM_DEG) / (2 * np.sqrt(2 * np.log(2)))
search_rad = np.radians(SEARCH_RADIUS_DEG)

print("=" * 60)
print("O2 STEP 2: ANTIPODE SCAN")
print("=" * 60)

# 1. Read and smooth SMICA
print(f"\n[1/4] Reading SMICA...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
print(f"  NSIDE = {nside}")

print(f"  Smoothing to {FWHM_DEG}° FWHM...")
m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
print(f"  Done.")

# 2. Antipode properties
print(f"\n[2/4] Antipode analysis")
print(f"  Cold spot:  (l, b) = ({COLD_SPOT[0]:.1f}°, {COLD_SPOT[1]:.1f}°)")
print(f"  Antipode:   (l, b) = ({ANTIPODE[0]:.1f}°, {ANTIPODE[1]:.1f}°)")

# Temperature at exact antipode
pix_anti = hp.ang2pix(nside, ANTIPODE[0], ANTIPODE[1], lonlat=True)
T_anti = m_s[pix_anti] * 1e6
print(f"  T at exact antipode: {T_anti:+.1f} μK")

# Temperature at cold spot for reference
pix_cold = hp.ang2pix(nside, COLD_SPOT[0], COLD_SPOT[1], lonlat=True)
T_cold = m_s[pix_cold] * 1e6
print(f"  T at cold spot:      {T_cold:+.1f} μK")

# 3. Scan 5° radius around antipode
print(f"\n[3/4] Scanning {SEARCH_RADIUS_DEG}° radius around antipode...")

# Get all pixels within search radius
vec_anti = hp.ang2vec(ANTIPODE[0], ANTIPODE[1], lonlat=True)
pix_disk = hp.query_disc(nside, vec_anti, search_rad)
T_disk = m_s[pix_disk] * 1e6

# Also compute angular distances for each pixel
vecs = hp.pix2vec(nside, pix_disk)
cos_angles = np.dot(vec_anti, np.array(vecs))
angles = np.arccos(np.clip(cos_angles, -1, 1))
angles_deg = np.degrees(angles)

print(f"  Pixels in search disk: {len(pix_disk):,}")

# Max temperature
max_idx = np.argmax(T_disk)
T_max = T_disk[max_idx]
l_max, b_max = hp.pix2ang(nside, pix_disk[max_idx], lonlat=True)
dist_max = angles_deg[max_idx]

print(f"\n  Maximum T in disk:")
print(f"    T = {T_max:+.1f} μK")
print(f"    at (l, b) = ({l_max:.2f}°, {b_max:.2f}°)")
print(f"    distance from antipode = {dist_max:.2f}°")

# Mean temperature in disk
mean_disk = np.mean(T_disk)
std_disk = np.std(T_disk)
print(f"  Mean T in disk: {mean_disk:+.1f} ± {std_disk:.1f} μK")
print(f"  # positive pixels: {np.sum(T_disk > 0):,} / {len(T_disk):,}")

# 4. Also check: is there a hot spot at the exact antipode distance?
# The cold spot's nearest node is 5.34° from antipode per SESSION_START.md
print(f"\n[4/4] Nearest 60-node position to antipode")
# Load nodes
NODES = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
COLORING = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt'

from astropy.coordinates import SkyCoord
import astropy.units as u

nodes_radec = np.loadtxt(NODES)
ra_deg, dec_deg = nodes_radec[:, 0], nodes_radec[:, 1]
sc = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg, frame='icrs')
gal = sc.galactic
l_nodes, b_nodes = gal.l.deg, gal.b.deg

# Angular distances from antipode
from scipy.spatial.distance import pdist, squareform
from scipy.spatial.distance import cdist
# Quick angular distance
vec_nodes = hp.ang2vec(l_nodes, b_nodes, lonlat=True)
cos_dists = np.dot(vec_nodes, vec_anti)
node_dists = np.degrees(np.arccos(np.clip(cos_dists, -1, 1)))

nearest = np.argmin(node_dists)
print(f"  Nearest node to antipode: node {nearest}")
print(f"    distance = {node_dists[nearest]:.2f}°")
print(f"    at (l,b) = ({l_nodes[nearest]:.2f}°, {b_nodes[nearest]:.2f}°)")

# Check hot/cold
coloring = np.loadtxt(COLORING, usecols=[0, 3])
node_colors = coloring[:, 1].astype(int)
node_hot = node_colors[nearest] == 0
print(f"    color = {'HOT' if node_hot else 'COLD'}")

# Temperature at nearest node
pix_near = hp.ang2pix(nside, l_nodes[nearest], b_nodes[nearest], lonlat=True)
T_near = m_s[pix_near] * 1e6
print(f"    T = {T_near:+.1f} μK")

# Also check all nodes within 5° of antipode
near_nodes = np.where(node_dists < SEARCH_RADIUS_DEG)[0]
print(f"\n  Nodes within {SEARCH_RADIUS_DEG}° of antipode ({len(near_nodes)}):")
for ni in near_nodes:
    c = 'HOT' if node_colors[ni] == 0 else 'COLD'
    pix_ni = hp.ang2pix(nside, l_nodes[ni], b_nodes[ni], lonlat=True)
    T_ni = m_s[pix_ni] * 1e6
    print(f"    node {ni:2d}  ({c})  dist={node_dists[ni]:.2f}°  T={T_ni:+.1f} μK")

# Summary
print(f"\n{'='*60}")
print(f"ANTIPODE SCAN SUMMARY")
print(f"{'='*60}")
print(f"  Cold spot T:          {T_cold:+.1f} μK")
print(f"  Exact antipode T:     {T_anti:+.1f} μK")
print(f"  Max in 5° disk:       {T_max:+.1f} μK at ({l_max:.1f}°, {b_max:.1f}°)")
print(f"  Mean in 5° disk:      {mean_disk:+.1f} μK")
print(f"  Nearest node T:       {T_near:+.1f} μK")
print(f"  Antipode vs cold:     {T_anti/T_cold:.3f} × cold spot")
print(f"  Max disk vs cold:     {T_max/T_cold:.3f} × cold spot")

# Fibonacci comparison
print(f"\n  Fibonacci predictions:")
F_levels = {'F₅': 150, 'F₆': 240, 'F₇': 390, 'F₈': 631}
for name, val in F_levels.items():
    print(f"    {name:6s} = {val:3.0f} μK  →  max_disk / ratio = {T_max/val:.3f}")

# Save results
with open(os.path.join(OUTDIR, 'antipode_scan.txt'), 'w') as f:
    f.write(f"# Antipode scan results\n")
    f.write(f"# Cold spot: (l,b)=({COLD_SPOT[0]},{COLD_SPOT[1]})\n")
    f.write(f"# Antipode: (l,b)=({ANTIPODE[0]},{ANTIPODE[1]})\n")
    f.write(f"# Search radius: {SEARCH_RADIUS_DEG}°\n")
    f.write(f"# Smoothing: {FWHM_DEG}° FWHM\n")
    f.write(f"T_cold_spot {T_cold:.1f}\n")
    f.write(f"T_antipode_exact {T_anti:.1f}\n")
    f.write(f"T_max_disk {T_max:.1f}\n")
    f.write(f"l_max {l_max:.2f}\n")
    f.write(f"b_max {b_max:.2f}\n")
    f.write(f"T_mean_disk {mean_disk:.1f}\n")
    f.write(f"T_std_disk {std_disk:.1f}\n")
    f.write(f"T_nearest_node {T_near:.1f}\n")
    f.write(f"nearest_node_idx {nearest}\n")

print(f"\n✅ Saved: data/antipode_scan.txt")
print(f"{'='*60}")
print(f"O2 STEP 2 COMPLETE")
print(f"{'='*60}")