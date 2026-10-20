#!/usr/bin/env python3
"""
O5 follow-up (node 9): multi-scale temperature profile — OPTIMIZED
===================================================================
Node 9 (ICRS 75.27,-15.21; Gal 214.92,-31.16):
  - BFS hop 1 from cold spot (direct neighbor)
  - color = hot (0), but ALL 4 neighbors cold (1) → 4 normal edges
  - 5.0° temperature: -105.0 μK (2nd coldest node!)
  - 1.0° catalogue: cold component peak 1.71° away → hit

Vectorized: single map read per scale, all 60 nodes sampled at once.
"""

import numpy as np
import healpy as hp
import os
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/smooth_cache')
import sys

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')

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

# CRITICAL: SMICA maps are in GALACTIC frame. Node coords are ICRS.
# MUST convert ICRS -> Galactic before sampling (O2 §4 pattern).
sc_all = SkyCoord(ra=NODES[:, 0] * u.deg, dec=NODES[:, 1] * u.deg, frame='icrs')
gal_all = sc_all.galactic
NODES_L = gal_all.l.deg
NODES_B = gal_all.b.deg

print("=" * 66)
print("NODE 9 DEEP DIVE — MULTI-SCALE TEMPERATURE PROFILE")
print("=" * 66)

scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]
print(f"\n{'scale':>6} {'node9 μK':>10} {'node0 μK':>10} {'node9 rank':>10}")
print("-" * 42)

node9_series = []
for fwhm in scales:
    m_s = smooth_map(fwhm)
    nside = hp.get_nside(m_s)
    T = m_s * 1e6
    pix = hp.ang2pix(nside, NODES_L, NODES_B, lonlat=True)
    node_vals = T[pix]
    v9 = node_vals[9]
    v0 = node_vals[0]
    rank = int(np.argsort(node_vals).tolist().index(9)) + 1
    node9_series.append(v9)
    print(f"{fwhm:>5}° {v9:>+10.1f} {v0:>+10.1f} {rank:>7}/60")

# Radial profile cold spot -> node9 at 1.0° smoothing
print(f"\nRadial profile cold spot → node9 (1.0° smoothing):")
m_s = smooth_map(1.0)
nside = hp.get_nside(m_s)
T = m_s * 1e6
v0 = hp.ang2vec(NODES_L[0], NODES_B[0], lonlat=True)
v9 = hp.ang2vec(NODES_L[9], NODES_B[9], lonlat=True)
for frac in np.linspace(0, 1, 11):
    v = v0 + frac * (v9 - v0)
    v = v / np.linalg.norm(v)
    lp, bp = hp.vec2ang(v, lonlat=True)
    lp, bp = float(lp[0]), float(bp[0])
    pix = hp.ang2pix(nside, lp, bp, lonlat=True)
    print(f"  {frac*100:>3.0f}% ({lp:6.2f},{bp:+6.2f}): {T[pix]:+7.1f} μK")

print(f"\nnode9 series: {[f'{t:+.1f}' for t in node9_series]}")
