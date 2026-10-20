#!/usr/bin/env python3
"""
O5 follow-up (node 9): is it a real second cold structure?
============================================================
Key facts so far:
  - node9 = ICRS (75.27,-15.21), Gal (214.92,-31.16), BFS hop 1 from cold spot
  - color = hot(0) but ALL 4 neighbors cold(1) → 4 normal edges (no frustration)
  - Multi-scale: cold at ≥1.5° (rank 4-11/60), warm at 0.5° (rank 42/60)
  - Radial profile: node9 sits at a SECOND local minimum (-117 μK) beyond a
    +75 μK ridge between it and the cold spot → SEPARATE structure

Tests:
  1. Local significance: is node9's large-scale coldness significant vs
     the smooth-map fluctuation field at its position (local σ)?
  2. Compare vs "neighbor of the cold spot" null: random offsets from
     node0 at 26° → what T distribution? (is a cold neighbor expected?)
  3. Antipodal check: node9's antipode — also cold? (mirror symmetry?)
"""

import numpy as np
import healpy as hp
import os
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/smooth_cache')
import json

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')
OUTDIR = f'{BASE}/data'

def smooth_map(fwhm):
    cache = f'{CACHE_DIR}/smica2_smooth{fwhm}.fits'
    if not os.path.exists(cache):
        m = hp.read_map('/tmp/smica2.fits', field=0)
        sig = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sig))
        hp.write_map(cache, m_s, overwrite=True)
    else:
        m_s = hp.read_map(cache, field=0)
    return m_s

from astropy.coordinates import SkyCoord
import astropy.units as u

# CRITICAL: SMICA maps are GALACTIC. Convert node ICRS -> Galactic (O2 §4).
sc_all = SkyCoord(ra=NODES[:, 0] * u.deg, dec=NODES[:, 1] * u.deg, frame='icrs')
gal_all = sc_all.galactic
NODES_L = gal_all.l.deg
NODES_B = gal_all.b.deg

print("=" * 66)
print("NODE 9 — SECOND COLD STRUCTURE?")
print("=" * 66)

FWHM = 3.0   # F5 regime, node9 rank 5/60 here
m_s = smooth_map(FWHM)
nside = hp.get_nside(m_s)
T = m_s * 1e6
l_arr, b_arr = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)), lonlat=True)
mask = np.abs(b_arr) >= 25
sig = np.std(T[mask])

# 1. Local significance at node9 (Galactic coords)
pix9 = hp.ang2pix(nside, NODES_L[9], NODES_B[9], lonlat=True)
T9 = T[pix9]
print(f"\n[1] node9 at 3.0°: T = {T9:+.1f} μK (global σ={sig:.1f} μK)")
print(f"    z = {T9/sig:+.2f}σ — NOT extreme by itself")

# 2. Null: random point at 26° from cold spot (in Galactic frame)
print(f"\n[2] Null test — random positions 26° from cold spot:")
rng = np.random.default_rng(9)
v0 = hp.ang2vec(NODES_L[0], NODES_B[0], lonlat=True)
Ts = []
for _ in range(2000):
    r = rng.normal(size=3)
    r = r - (r @ v0) * v0
    r = r / np.linalg.norm(r)
    v = np.cos(np.radians(26.166)) * v0 + np.sin(np.radians(26.166)) * r
    pix = hp.vec2pix(nside, *v)
    if abs(b_arr[pix]) < 25:
        continue
    Ts.append(T[pix])
Ts = np.array(Ts)
p = (Ts <= T9).mean()
print(f"    T at 26° ring: mean={Ts.mean():+.1f}, std={Ts.std():+.1f} μK")
print(f"    node9 T={T9:+.1f} → percentile {p*100:.1f}% (p={p:.3f}) "
      f"{'🟢 cold' if p < 0.05 else '— not special'}")

# 3. Antipode of node9 (in Galactic frame)
print(f"\n[3] Antipode of node9:")
anti = -hp.ang2vec(NODES_L[9], NODES_B[9], lonlat=True)
la, ba = hp.vec2ang(anti, lonlat=True)
la, ba = la[0], ba[0]
pix_a = hp.ang2pix(nside, la, ba, lonlat=True)
print(f"    antipode (l,b)=({la:.2f},{ba:+.2f}) → T={T[pix_a]:+.1f} μK")

# 4. Compare with all other nodes' 3.0° temps
print(f"\n[4] All 60 nodes at 3.0° (coldest 10):")
pix_all = hp.ang2pix(nside, NODES_L, NODES_B, lonlat=True)
node_T = T[pix_all]
order = np.argsort(node_T)
for i in order[:10]:
    print(f"    node{i}: {node_T[i]:+7.1f} μK")
