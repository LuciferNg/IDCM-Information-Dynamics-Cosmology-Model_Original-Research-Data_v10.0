#!/usr/bin/env python3
"""
O5 Step 2c: SMICA all-sky cold/hot spot catalogue — HEALPix flood-fill
======================================================================
CRITICAL FIXES over naive ndimage.label:
1. ndimage.label treats the HEALPix array as a flat image — pixels are NOT
   neighbours in array order (ring ordering). It produced 0 components for
   1.3M thresholded pixels. MUST use healpy's `hp.query_disc` flood-fill
   (or hp.sphtfunc adjacency) for true spherical connected components.
2. Use the RIGHT smoothing scale: O2's multiscale scan shows the Cold Spot
   peak at 3.0-5.0° (F₅ best at 3.0°: -145 μK; 5.0°: -124.6 μK).
   We use 5.0° (the O2-verified 01_hot_node_mean scale, node0 = -124.6 μK).
3. Fixed μK thresholds relative to the smoothed map's σ (|b|>25°).

Algorithm (spherical flood-fill):
  for each unvisited pixel below/above threshold:
    BFS/DFS: expand to all neighbours (8 healpix neighbours via
    hp.get_all_neighbours) that also pass the threshold
  each connected component = one spot; peak = extremal pixel
"""

import numpy as np
import healpy as hp
import json
import os
from collections import deque

SMICA = '/tmp/smica2.fits'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data'
os.makedirs(OUTDIR, exist_ok=True)

FWHM_DEG = 5.0        # O2-verified scale: node0 (cold spot) = -124.6 μK here
SIGMA_RAD = np.radians(FWHM_DEG) / (2 * np.sqrt(2 * np.log(2)))
MASK_B = 25.0
N_SIGMA = 2.0         # threshold in σ of unmasked sky
MIN_AREA = 2.0        # deg² — minimum component area
MERGE_RAD = 5.0       # deg — merge peaks of same structure

print("=" * 66)
print("O5 STEP 2c: SMICA CATALOGUE — SPHERICAL FLOOD-FILL")
print("=" * 66)

# 1. Smooth map at 5.0° (cache per-scale to avoid re-smoothing)
# NOTE: use '.1f' naming (5.0) to match scripts 05/06/08 cache keys
CACHE5 = os.path.join(BASE_DIR, 'smica2_smooth5.0.fits')
if os.path.exists(CACHE5):
    print(f"Using cached 5.0°-smoothed map")
    m_s = hp.read_map(CACHE5, field=0)
else:
    print(f"Smoothing raw SMICA at {FWHM_DEG}°...")
    m = hp.read_map(SMICA, field=0)
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=SIGMA_RAD))
    hp.write_map(CACHE5, m_s, overwrite=True)
    print("  cached.")

nside = hp.get_nside(m_s)
T = m_s * 1e6
npix = hp.nside2npix(nside)
l_arr, b_arr = hp.pix2ang(nside, np.arange(npix), lonlat=True)
mask_gal = np.abs(b_arr) < MASK_B
Tv = T[~mask_gal]
sigma = np.std(Tv)
th = N_SIGMA * sigma
print(f"NSIDE={nside}, 5.0° smoothed: σ={sigma:.1f} μK (|b|≥{MASK_B}°), "
      f"threshold=±{th:.1f} μK (±{N_SIGMA}σ)")


def flood_fill(kind):
    """Spherical connected components. kind='cold' or 'hot'.
    Returns list of dicts: peak_l, peak_b, amp, area_deg2, n_pix."""
    if kind == 'cold':
        pass_mask = T < -th
    else:
        pass_mask = T > th
    pass_mask = pass_mask & ~mask_gal

    visited = np.zeros(npix, dtype=bool)
    comps = []
    pix_area = hp.nside2pixarea(nside)

    # Precompute neighbours (8 per pixel) once
    nbrs = hp.get_all_neighbours(nside, np.arange(npix))  # shape (8, npix)

    for start in np.where(pass_mask)[0]:
        if visited[start]:
            continue
        # BFS
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
        area_deg2 = len(comp) * pix_area * (180 / np.pi) ** 2
        if area_deg2 < MIN_AREA:
            continue
        if kind == 'cold':
            peak_pix = comp[np.argmin(T[comp])]
        else:
            peak_pix = comp[np.argmax(T[comp])]
        lp, bp = hp.pix2ang(nside, peak_pix, lonlat=True)
        comps.append(dict(
            peak_l=float(lp), peak_b=float(bp),
            amp_muK=float(T[peak_pix]), area_deg2=float(area_deg2),
            n_pix=len(comp)))
    return comps


def merge_peaks(comps, merge_rad):
    """Vectorized merge of peaks within merge_rad."""
    if not comps:
        return []
    thetas = np.radians(90 - np.array([c['peak_b'] for c in comps]))
    phis = np.radians(np.array([c['peak_l'] for c in comps]))
    vecs = np.stack([np.sin(thetas) * np.cos(phis),
                     np.sin(thetas) * np.sin(phis),
                     np.cos(thetas)], axis=1)
    merged = []
    kept = np.zeros(len(comps), dtype=bool)
    for idx in np.argsort([-abs(c['amp_muK']) for c in comps]):
        if kept[idx]:
            continue
        kept[idx] = True
        merged.append(comps[idx])
        dots = np.clip(vecs @ vecs[idx], -1.0, 1.0)
        kept[np.degrees(np.arccos(dots)) < merge_rad] = True
    return merged


print(f"\n[2/4] Flood-fill components at ±{th:.1f} μK...")
catalog = {'cold': [], 'hot': []}
for kind in ['cold', 'hot']:
    comps = flood_fill(kind)
    print(f"  {kind}: {len(comps)} components (area≥{MIN_AREA}°²)")
    merged = merge_peaks(comps, MERGE_RAD)
    print(f"  {kind}: {len(merged)} after merging within {MERGE_RAD}°")
    catalog[kind] = merged

# 3. ICRS conversion
from astropy.coordinates import SkyCoord
import astropy.units as u
for kind in ['cold', 'hot']:
    for s in catalog[kind]:
        c = SkyCoord(l=s['peak_l'] * u.deg, b=s['peak_b'] * u.deg, frame='galactic')
        icrs = c.icrs
        s['peak_ra'] = float(icrs.ra.deg)
        s['peak_dec'] = float(icrs.dec.deg)

# 4. Sanity: cold spot must be in catalogue
cs_found = any(abs(s['peak_l'] - 209) < 8 and abs(s['peak_b'] + 57) < 8
               for s in catalog['cold'])
print(f"\n[4/4] Cold Spot (209,-57) in catalogue: {cs_found}")

with open(os.path.join(OUTDIR, 'smica_catalog.json'), 'w') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"\nSaved: data/smica_catalog.json")
print(f"{'kind':<6} {'#':>2} {'amp μK':>9} {'l°':>8} {'b°':>8} {'RA°':>8} {'Dec°':>8} {'area°²':>8}")
for kind in ['cold', 'hot']:
    for i, s in enumerate(catalog[kind], 1):
        warn = " <-- gal plane" if abs(s['peak_b']) < 30 else ""
        print(f"{kind:<6} {i:>2} {s['amp_muK']:+9.1f} {s['peak_l']:>8.2f} "
              f"{s['peak_b']:>+8.2f} {s['peak_ra']:>8.2f} {s['peak_dec']:>+8.2f} "
              f"{s['area_deg2']:>8.1f}{warn}")
