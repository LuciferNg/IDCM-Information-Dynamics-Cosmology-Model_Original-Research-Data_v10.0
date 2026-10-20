#!/usr/bin/env python3
"""
O5 Step 5: Scale matching + special-position checks
=====================================================
1. Scale check: catalogue spot angular sizes vs node influence radius.
   Node spacing 26.09°, each node's Voronoi cell radius ≈ 13.05°.
   The Cold Spot (4.17° FWHM at R8) fits comfortably INSIDE a node cell.
   Large SMICA components (area 100+ deg²) span multiple cells → these
   are large-scale CMB fluctuations, NOT node-scale structure.

2. Special-position check: do the SMICA catalogue peaks coincide with
   the O2-verified Fibonacci hot spots?
   - F₆ hot spot: (157.8°, -70.3°) @ 1.0° smoothing (O2 confirmed)
   - F₇ hot spot: (0.2°, -37.9°) @ 0.5° smoothing (O2 candidate)
   These are at DIFFERENT scales than our 5.0° catalogue — check anyway.

3. Cross-scale catalogues: re-extract cold/hot peaks at 1.0° and 3.0°
   (the F₆/F₅ scales) and check node alignment — a node might host a
   hot spot at fine scale even if the 5.0° map shows nothing.
"""

import numpy as np
import healpy as hp
import json
import os
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/smooth_cache')

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')
OUTDIR = f'{BASE}/data'

node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([
    np.cos(node_dec) * np.cos(node_ra),
    np.cos(node_dec) * np.sin(node_ra),
    np.sin(node_dec)], axis=1)

def nearest_node(ra_deg, dec_deg):
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    v = np.array([np.cos(dec) * np.cos(ra),
                  np.cos(dec) * np.sin(ra),
                  np.sin(dec)])
    dots = np.clip(node_vecs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return float(d.min()), int(d.argmin())

print("=" * 66)
print("O5 STEP 5: SCALE MATCHING + SPECIAL POSITIONS")
print("=" * 66)

# 1. Scale check
sm = json.load(open(f'{OUTDIR}/smica_catalog.json'))
print("\n[1/3] SMICA 5.0° component areas vs node cell size")
print(f"  Node spacing = 26.09°, Voronoi cell radius ≈ 13.05°")
print(f"  Cold Spot FWHM (R8) = 4.17° → fits inside one cell ✅")
for kind in ['cold', 'hot']:
    areas = np.array([s['area_deg2'] for s in sm[kind]])
    big = (areas > 100).sum()
    print(f"  {kind}: {len(areas)} spots, area range {areas.min():.1f}-{areas.max():.1f}°², "
          f"{big} large (>100°² = multi-cell)")

# 2. O2 Fibonacci hot spots — check node alignment
print("\n[2/3] O2 Fibonacci hot spots vs A₅ nodes")
o2_spots = [
    ('F₆ hot (157.8,-70.3) @1.0°', 157.8, -70.3, '+277.6 μK', 'confirmed'),
    ('F₇ hot (0.2,-37.9) @0.5°', 0.2, -37.9, '+353.4 μK', 'candidate'),
]
from astropy.coordinates import SkyCoord
import astropy.units as u
for name, l, b, amp, status in o2_spots:
    c = SkyCoord(l=l*u.deg, b=b*u.deg, frame='galactic').icrs
    d, n = nearest_node(c.ra.deg, c.dec.deg)
    print(f"  {name}: {amp} ({status}) → nearest node {n} at {d:.2f}° "
          f"{'✅ HIT' if d < 5 else '—'}")

# 3. Cross-scale peak extraction (1.0°, 3.0° smoothing)
print("\n[3/3] Cross-scale catalogue (1.0° & 3.0° — F₆/F₅ scales)")
from scipy import ndimage

for fwhm in [1.0, 3.0]:
    cache = f'{CACHE_DIR}/smica2_smooth{fwhm}.fits'
    if not os.path.exists(cache):
        m = hp.read_map('/tmp/smica2.fits', field=0)
        sig = np.radians(fwhm) / (2 * np.sqrt(2 * np.log(2)))
        m_s = hp.remove_dipole(hp.smoothing(m, sigma=sig))
        hp.write_map(cache, m_s, overwrite=True)
    else:
        m_s = hp.read_map(cache, field=0)
    nside = hp.get_nside(m_s)
    T = m_s * 1e6
    l_arr, b_arr = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)), lonlat=True)
    mask = np.abs(b_arr) >= 25
    sigma = np.std(T[mask])

    # Find top 10 cold + hot peaks (pixel maxima, not components)
    # NOTE: argsort(sign*T) is WRONG — argsort(-T) picks the LARGEST T.
    # Correct: cold = argsort(T)[:10] (smallest = coldest),
    #          hot  = argsort(-T)[:10] (largest = hottest).
    for kind in ['cold', 'hot']:
        T_masked = np.where(mask, T, np.nan)
        if kind == 'cold':
            order = np.argsort(T_masked)[:10]
        else:
            order = np.argsort(-T_masked)[:10]
        n_hit = 0
        for p in order:
            lp, bp = hp.pix2ang(nside, p, lonlat=True)
            c = SkyCoord(l=lp*u.deg, b=bp*u.deg, frame='galactic').icrs
            d, n = nearest_node(c.ra.deg, c.dec.deg)
            if d < 5:
                n_hit += 1
        print(f"  {fwhm:.1f}° {kind} top10 peaks: {n_hit}/10 within 5° of a node "
              f"(random expect ~1.1) {'🟢' if n_hit >= 4 else '🟡' if n_hit >= 2 else '🔴'}")

print("\n  Random expectation: 10 peaks × 11.4% coverage ≈ 1.1 hits")
