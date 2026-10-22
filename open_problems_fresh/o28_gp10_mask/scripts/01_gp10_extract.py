#!/usr/bin/env python3
"""
O28 Script 01: gp10 cold region extraction + mask correction
============================================================
Goal: Planck 2013 gp10 region (l=32°, b=-8°, fsky=7%, partially masked
by Galactic plane). Extract the actual cold component from SMICA at the
structure's own scale, then compute the mask-corrected centroid.

Key points:
- gp10 sits at b=-8° -> INSIDE the |b|<20° galactic mask zone. O5's
  catalogue (|b|>25°) never included it — that's why O28 exists.
- Flood-fill at nside=1024 (memory-safe; smoothed structure is 5-10°,
  0.057°/pix at nside 1024 is ample).
- Mask correction: recompute centroid over UNMASKED pixels only
  (|b| >= b_cut) and see where it shifts.
- Cross-check with NILC/Commander caches (foreground-suspect region).
"""
import numpy as np
import healpy as hp
import json, os
from collections import deque

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
CACHE = BASE + '/o5_catalog_compare/data/smooth_cache'
OUT = BASE + '/o28_gp10_mask/data'
os.makedirs(OUT, exist_ok=True)

GP_L, GP_B = 32.0, -8.0
SEARCH_RAD = 25.0          # search radius around gp10 centre
FWHM_LIST = [3.0, 4.17, 5.0, 7.0]

def load_smoothed(name):
    p = f'{CACHE}/{name}'
    m = hp.read_map(p, field=0)
    return m

def ud(m, nside_out=1024):
    """Downsample to nside 1024 for memory-safe flood-fill."""
    nside = hp.get_nside(m)
    if nside == nside_out:
        return m
    return hp.ud_grade(m, nside_out=nside_out)

def flood_fill_near(m, l0, b0, search_rad, threshold, b_cut):
    """Flood-fill cold components within search_rad of (l0,b0),
    using pixels with |b|>=b_cut only. Returns list of comps."""
    nside = hp.get_nside(m)
    npix = hp.nside2npix(nside)
    pix_area = hp.nside2pixarea(nside)
    # mask: within search radius of gp10, |b|>=b_cut, below threshold
    disc = hp.query_disc(nside, hp.ang2vec(np.radians(90-GP_B), np.radians(GP_L)),
                         np.radians(search_rad))
    l_arr, b_arr = hp.pix2ang(nside, disc, lonlat=True)
    pass_mask = np.zeros(npix, dtype=bool)
    sel = (m[disc] < threshold) & (np.abs(b_arr) >= b_cut)
    pass_mask[disc[sel]] = True

    # neighbours for flood fill (restricted to the disc subset)
    nbrs = hp.get_all_neighbours(nside, disc)  # (8, ndisc)
    valid = nbrs >= 0
    # map disc index -> global pixel
    disc_pix = disc
    # convert neighbour global pixels to membership in disc via searchsorted
    disc_sorted = np.sort(disc)
    idx_of = np.searchsorted(disc_sorted, nbrs)
    in_disc = (idx_of < len(disc_sorted)) & (disc_sorted[np.clip(idx_of, 0, len(disc_sorted)-1)] == nbrs)

    visited = np.zeros(len(disc), dtype=bool)
    comps = []
    for i in np.where(pass_mask[disc])[0]:
        if visited[i]:
            continue
        comp = []
        q = deque([i])
        visited[i] = True
        while q:
            p = q.popleft()
            comp.append(disc[p])
            for k in range(8):
                if not valid[k, p] or not in_disc[k, p]:
                    continue
                j = int(idx_of[k, p])
                if not visited[j] and pass_mask[disc[j]]:
                    visited[j] = True
                    q.append(j)
        if len(comp) < 5:
            continue
        Tcomp = m[comp]
        peak = comp[np.argmin(Tcomp)]
        lp, bp = hp.pix2ang(nside, peak, lonlat=True)
        # centroid over unmasked pixels of this comp
        comp_b = hp.pix2ang(nside, np.array(comp), lonlat=True)[1]
        unmasked = np.array(comp)[np.abs(comp_b) >= b_cut]
        # centroid via unit vectors
        v = hp.pix2vec(nside, unmasked)
        vc = np.mean(v, axis=1)
        vc /= np.linalg.norm(vc)
        cl, cb = hp.vec2ang(vc, lonlat=True)
        cl = float(np.atleast_1d(cl)[0]); cb = float(np.atleast_1d(cb)[0])
        comps.append(dict(
            peak_l=float(lp), peak_b=float(bp), amp_muK=float(Tcomp.min()*1e6),
            n_pix=len(comp), area_deg2=float(len(comp)*pix_area*(180/np.pi)**2),
            cent_l=float(cl), cent_b=float(cb),
            n_unmasked=len(unmasked)))
    return comps

results = {}
for fwhm in FWHM_LIST:
    name = f'smica2_smooth{fwhm}.fits'
    if not os.path.exists(f'{CACHE}/{name}'):
        continue
    m = load_smoothed(name)
    m10 = ud(m)
    nside = hp.get_nside(m10)
    # sigma over unmasked sky (|b|>25 like O5) for threshold
    l_all, b_all = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)), lonlat=True)
    sky = np.abs(b_all) >= 25
    sigma = np.std(m10[sky])
    th = 1.5 * sigma
    row = {}
    for b_cut in [5, 10, 15, 20]:
        comps = flood_fill_near(m10, GP_L, GP_B, SEARCH_RAD, -th, b_cut)
        comps.sort(key=lambda c: c['amp_muK'])
        row[f'bcut{b_cut}'] = comps
    results[f'{fwhm}°'] = row
    print(f"\n=== FWHM {fwhm}° (nside={nside}, σ={sigma*1e6:.1f} μK, th={th*1e6:.1f} μK) ===")
    for b_cut, comps in row.items():
        print(f"  {b_cut}: {len(comps)} cold comps near gp10")
        for c in comps[:3]:
            print(f"    peak ({c['peak_l']:.1f},{c['peak_b']:+.1f}) "
                  f"amp={c['amp_muK']:+.1f} area={c['area_deg2']:.0f}°² "
                  f"centroid({c['cent_l']:.1f},{c['cent_b']:+.1f}) unmasked={c['n_unmasked']}")

with open(f'{OUT}/gp10_extract.json', 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT}/gp10_extract.json")
