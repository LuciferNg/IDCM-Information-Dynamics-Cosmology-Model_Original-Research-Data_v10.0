#!/usr/bin/env python3
"""
O28 Script 02: Planck-style Nside=16 analysis + fine-scale scan of gp10
=======================================================================
Planck 2013 XXIII analysed gp10 at Nside=16 (3.7°/pixel): high variance
+ negative skewness -> "cold spot at b=-8, l=32, partially masked".

Reproduce:
1. Nside=16 map, gp10 region (fsky=7% ~ 2944 deg², radius ~30.6°):
   variance / skewness / kurtosis of the region, compare vs rest of sky.
2. Fine-scale scan (0.5-3.0°) of temperature around (32,-8): is there
   a small-scale cold spot the 4.17°+ smoothing erased?
3. Radial profile out to 30°: where is the cold structure, if any?
"""
import numpy as np
import healpy as hp
import json, os

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
CACHE = BASE + '/o5_catalog_compare/data/smooth_cache'
OUT = BASE + '/o28_gp10_mask/data'

GP_L, GP_B = 32.0, -8.0
# Planck: gp10 = fsky 7%. A 30°-radius cap covers 6.7% of sky; use 30°.
R_GP10 = 30.0
print(f"gp10 region: r={R_GP10}° (fsky={0.5*(1-np.cos(np.radians(R_GP10))):.1%})")

# ---- 1. Nside=16 Planck-style analysis (SMICA 4.17° degraded) ----
m16 = hp.ud_grade(hp.read_map(f'{CACHE}/smica2_smooth4.17.fits', field=0), nside_out=16)
nside16 = 16
npix16 = hp.nside2npix(nside16)
l16, b16 = hp.pix2ang(nside16, np.arange(npix16), lonlat=True)
vec_gp = hp.ang2vec(np.radians(90-GP_B), np.radians(GP_L))
disc = hp.query_disc(nside16, vec_gp, np.radians(R_GP10))
T16 = m16[disc]*1e6
sky_mask = np.abs(b16) >= 5   # keep the analysis honest: |b|>=5 around gp10
# Note: Planck used specific masks; we use gp10-region vs rest-of-sky

# region stats
reg = T16
rest = m16[np.abs(b16) >= 25]*1e6
def stats(x):
    return dict(mean=float(np.mean(x)), var=float(np.var(x)),
                skew=float(__import__('scipy').stats.skew(x)) if len(x)>2 else 0,
                kurt=float(__import__('scipy').stats.kurtosis(x)) if len(x)>2 else 0,
                n=len(x))
print("\n=== Nside=16 Planck-style ===")
print(f"gp10 region (r={R_GP10:.1f}°, {len(reg)} pix): {stats(reg)}")
print(f"rest of sky |b|>=25 ({len(rest)} pix): {stats(rest)}")
print(f"gp10 var / rest var = {np.var(reg)/np.var(rest):.2f}")

# ---- 2. Fine-scale scan: peak cold pixel within radius around gp10 ----
print("\n=== Fine-scale scan (peak cold within 15° of gp10) ===")
fine = {}
for fwhm in [0.5, 1.0, 1.5, 2.0, 3.0]:
    p = f'{CACHE}/smica2_smooth{fwhm}.fits'
    if not os.path.exists(p):
        continue
    m = hp.read_map(p, field=0)
    nside = hp.get_nside(m)
    # search disc radius 15°
    d = hp.query_disc(nside, vec_gp, np.radians(15))
    Td = m[d]*1e6
    i = np.argmin(Td)
    lp, bp = hp.pix2ang(nside, d[i], lonlat=True)
    fine[f'{fwhm}°'] = dict(peak_l=float(lp), peak_b=float(bp),
                            amp=float(Td[i]), mean=float(Td.mean()),
                            median=float(np.median(Td)),
                            pct1=float(np.percentile(Td,1)))
    print(f"  FWHM {fwhm}°: peak ({lp:.1f},{bp:+.1f}) = {Td[i]:+.1f} μK | "
          f"region mean {Td.mean():+.1f}, pct1 {np.percentile(Td,1):+.1f}")

# ---- 3. Radial profile of SMICA 4.17° around gp10 ----
print("\n=== Radial profile (4.17°) around gp10 ===")
m417 = hp.read_map(f'{CACHE}/smica2_smooth4.17.fits', field=0)
nside = hp.get_nside(m417)
radial = {}
for r0 in [0, 5, 10, 15, 20, 25, 30]:
    ring = hp.query_disc(nside, vec_gp, np.radians(r0+5)) 
    inner = hp.query_disc(nside, vec_gp, np.radians(r0)) if r0 > 0 else np.array([], dtype=int)
    shell = np.setdiff1d(ring, inner)
    if len(shell) == 0:
        continue
    Ts = m417[shell]*1e6
    radial[f'{r0}-{r0+5}°'] = dict(mean=float(Ts.mean()), std=float(Ts.std()),
                                   n=int(len(shell)))
    print(f"  {r0}-{r0+5}°: mean {Ts.mean():+.1f} ± {Ts.std():.1f} (n={len(shell)})")

with open(f'{OUT}/gp10_planck_style.json', 'w') as f:
    json.dump(dict(r_gp10=R_GP10, nside16_stats=dict(region=stats(reg), rest=stats(rest)),
                   fine=fine, radial=radial), f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT}/gp10_planck_style.json")
