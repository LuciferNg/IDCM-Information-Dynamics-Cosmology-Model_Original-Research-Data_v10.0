#!/usr/bin/env python3
"""
O5 Step 6b: Cross-scale catalogue matching — MEMORY-EFFICIENT flood-fill
========================================================================
FIX (2026-08-17 OOM): hp.get_all_neighbours(nside, np.arange(npix)) on
nside=2048 (50M pixels) allocates 8×50M int64 = 3.2 GB → cgroup OOM kill.

Efficient alternative: precompute neighbours ONCE per scale in int32 with
chunked processing, or better — use healpy's built-in neighbourhood via
pixel-ring arithmetic (RING ordering allows O(1) neighbour lookup without
a full 8×npix matrix).

Simplest robust fix: process components via scipy.ndimage on a DOWNGRADED
map. nside=1024 (12.6M px) keeps structure at 4°+ scales and cuts memory
8×. The catalogue is scale-limited anyway (we only care about components
with area ≥ 1-2 deg², which are ≥ 1000 px at nside=1024).

Actually the cleanest: reuse hp.query_disc per seed is too slow. Instead:
  - build neighbour list in int32 (halves memory: 1.6 GB)
  - OR chunk: process pixels in bands of rings (RING order: neighbours
    stay within ±2 rings), freeing the full matrix.

We use the int32 + freed-matrix approach:
  1. nbrs = hp.get_all_neighbours(...).astype(np.int32)  (1.6 GB)
  2. flood-fill, then del nbrs before next scale.
"""

import numpy as np
import healpy as hp
import json
import os
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/smooth_cache')
import gc
from collections import deque
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')
OUTDIR = f'{BASE}/data'
HIT_RADIUS = 5.0

# CRITICAL: SMICA is GALACTIC. Convert ICRS -> Galactic.
sc_all = SkyCoord(ra=NODES[:, 0] * u.deg, dec=NODES[:, 1] * u.deg, frame='icrs')
gal_all = sc_all.galactic
NODES_L = gal_all.l.deg
NODES_B = gal_all.b.deg

node_ra = np.radians(NODES_L)
node_dec = np.radians(NODES_B)
node_vecs = np.stack([np.cos(node_dec) * np.cos(node_ra),
                      np.cos(node_dec) * np.sin(node_ra),
                      np.sin(node_dec)], axis=1)

def nearest_node(l_deg, b_deg):
    v = hp.ang2vec(l_deg, b_deg, lonlat=True)
    dots = np.clip(node_vecs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return float(d.min()), int(d.argmin())

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

def flood_fill_mem(T, sign, th, mask_gal, nside, min_area=1.0):
    """Spherical connected components — SAME as 02's flood_fill (int64).

    調律者指示 (2026-08-17): int32 精度風險唔值得慳嗰 1.6GB —
    保持 int64 完全一致。OOM 避開方式係喺 caller 逐個 scale
    用完整 map 跑, 每張 map 用完即 del + gc (唔累積三張 map)。"""
    npix = len(T)
    if sign > 0:
        pass_mask = (T > th) & mask_gal
    else:
        pass_mask = (T < -th) & mask_gal

    visited = np.zeros(npix, dtype=bool)
    pix_area = hp.nside2pixarea(nside)

    print(f"    [mem] building int64 neighbours ({npix/1e6:.0f}M px)...")
    nbrs = hp.get_all_neighbours(nside, np.arange(npix))  # int64, 3.2 GB
    print(f"    [mem] nbrs array: {nbrs.nbytes/1e9:.2f} GB")

    comps = []
    n_comp = 0
    for start in np.where(pass_mask)[0]:
        if visited[start]:
            continue
        comp = []
        q = deque([start])
        visited[start] = True
        while q:
            p = q.popleft()
            comp.append(p)
            for nb in nbrs[:, p]:
                if nb >= 0 and not visited[nb] and pass_mask[nb]:
                    visited[nb] = True
                    q.append(nb)
        n_comp += 1
        area = len(comp) * pix_area * (180 / np.pi) ** 2
        if area >= min_area:
            comps.append(comp)

    del nbrs
    gc.collect()
    return comps

print("=" * 66)
print("O5 STEP 6b: CROSS-SCALE MATCHING (MEMORY-EFFICIENT)")
print("=" * 66)

CONFIG = [(1.0, 2.5), (3.0, 2.0), (5.0, 2.0)]
summary = {}
for fwhm, th_sigma in CONFIG:
    m_s = smooth_map(fwhm)
    nside = hp.get_nside(m_s)
    T = m_s * 1e6
    l_arr, b_arr = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)), lonlat=True)
    mask_gal = np.abs(b_arr) >= 25
    sigma = np.std(T[mask_gal])

    print(f"\n--- {fwhm}° smoothing (σ={sigma:.1f} μK, ±{th_sigma}σ) ---")
    scale_hits = {'cold': [], 'hot': []}
    for kind, sign in [('cold', -1), ('hot', +1)]:
        # full-res flood-fill (identical to 02), int32 neighbours to halve
        # the matrix, freed after each call to avoid OOM accumulation
        comps = flood_fill_mem(T, sign, th_sigma * sigma, mask_gal, nside)
        comps.sort(key=lambda c: T[c].min() if sign < 0 else -T[c].max())
        top = comps[:12]
        hits = []
        for c in top:
            pk = c[np.argmin(T[c])] if sign < 0 else c[np.argmax(T[c])]
            lp, bp = hp.pix2ang(nside, pk, lonlat=True)
            lp, bp = float(lp), float(bp)
            d, n = nearest_node(lp, bp)
            area = len(c) * hp.nside2pixarea(nside) * (180 / np.pi) ** 2
            hits.append(dict(l=lp, b=bp, amp=float(T[pk]),
                             node=int(n), dist=float(d), area=float(area)))
        n_hit = sum(1 for h in hits if h['dist'] < HIT_RADIUS)
        nodes = sorted({h['node'] for h in hits if h['dist'] < HIT_RADIUS})
        scale_hits[kind] = dict(n_comp=len(comps), top12=n_hit, nodes=nodes,
                                details=hits)
        print(f"  {kind}: {len(comps)} comps, top12 → {n_hit}/12 hit "
              f"(random ≈ 1.4) nodes={nodes}")
        del comps, top, hits
    summary[str(fwhm)] = scale_hits
    # 每 scale 完即釋放大 array (防三張 map + l/b 累積 OOM)
    del m_s, T, l_arr, b_arr, mask_gal
    gc.collect()

with open(f'{OUTDIR}/cross_scale_match.json', 'w') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"\n{'=' * 66}")
print("SUMMARY — all scales, all kinds")
print("=" * 66)
print(f"{'scale':>6} {'kind':<5} {'comps':>5} {'hits/12':>8} {'nodes':<22}")
for fwhm, sh in summary.items():
    for kind in ['cold', 'hot']:
        d = sh[kind]
        print(f"{fwhm:>5}° {kind:<5} {d['n_comp']:>5} {d['top12']:>5}/12 "
              f"{str(d['nodes']):<22}")
print(f"\nRandom expectation per 12: 12 × 11.4% ≈ 1.4 hits")
print(f"Saved: data/cross_scale_match.json")
