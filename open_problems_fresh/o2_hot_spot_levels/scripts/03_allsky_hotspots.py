#!/usr/bin/env python3
"""
O2 Step 3: All-sky hot spot search
===================================
Find the hottest pixels on 5° smoothed SMICA and compare to
Fibonacci predictions: F₆=240μK, F₇=390μK, F₈=631μK.

Uses connected-component analysis to find discrete hot spots.
"""

import numpy as np
import healpy as hp
from scipy import ndimage
import sys, os

SMICA = '/tmp/smica2.fits'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/data'
os.makedirs(OUTDIR, exist_ok=True)

FWHM_DEG = 5.0
sigma_rad = np.radians(FWHM_DEG) / (2 * np.sqrt(2 * np.log(2)))

# Fibonacci predictions
F_LEVELS = {'F₅': 150.0, 'F₆': 240.0, 'F₇': 390.0, 'F₈': 631.0}

print("=" * 60)
print("O2 STEP 3: ALL-SKY HOT SPOT SEARCH")
print("=" * 60)

# 1. Read and smooth SMICA
print(f"\n[1/5] Reading SMICA...")
m = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m)
print(f"  NSIDE = {nside}")

m_s = hp.remove_dipole(hp.smoothing(m, sigma=sigma_rad))
T = m_s * 1e6  # μK
print(f"  Smoothed map: min={T.min():+.1f} μK, max={T.max():+.1f} μK, std={np.std(T):.1f} μK")

# 2. Find all-sky maximum
print(f"\n[2/5] All-sky maximum temperature")
max_idx = np.argmax(T)
l_max, b_max = hp.pix2ang(nside, max_idx, lonlat=True)
T_max = T[max_idx]
print(f"  Global maximum: {T_max:+.1f} μK at (l, b) = ({l_max:.2f}°, {b_max:.2f}°)")

# Report top 20 hottest pixels with their positions
print(f"\n  Top 20 hottest pixels:")
sorted_pix = np.argsort(T)[::-1]
for rank in range(20):
    pi = sorted_pix[rank]
    li, bi = hp.pix2ang(nside, pi, lonlat=True)
    Ti = T[pi]
    print(f"    #{rank+1:2d}: {Ti:+7.1f} μK  at (l={li:7.2f}°, b={bi:7.2f}°)")

# 3. Threshold-based hot spot identification
print(f"\n[3/5] Connected-component hot spot analysis")

# Multiple thresholds
for threshold in [20, 30, 40, 50, 60, 80, 100, 120, 150]:
    mask = T > threshold
    n_pix = np.sum(mask)
    if n_pix == 0:
        print(f"  Threshold > {threshold} μK: 0 pixels")
        continue
    
    # Label connected components
    labeled, n_features = ndimage.label(mask)
    print(f"  Threshold > {threshold:3d} μK: {n_pix:>8,} pixels, {n_features:>4d} hot spots")
    
    if n_features > 0 and n_features <= 20:
        for feat in range(1, n_features + 1):
            feat_mask = (labeled == feat)
            feat_pix = np.where(feat_mask)[0]
            feat_T = T[feat_pix]
            peak = feat_T.max()
            peak_pix = feat_pix[np.argmax(feat_T)]
            lp, bp = hp.pix2ang(nside, peak_pix, lonlat=True)
            area_sr = len(feat_pix) * hp.nside2pixarea(nside)
            area_deg2 = area_sr * (180/np.pi)**2
            print(f"    Spot #{feat:2d}: peak={peak:+6.1f} μK @ ({lp:7.2f}°, {bp:6.2f}°), area={area_deg2:.0f} deg²")

# 4. Compare maximum to Fibonacci predictions
print(f"\n[4/5] Fibonacci comparison")
print(f"  Global maximum: {T_max:+.1f} μK")
for name, val in F_LEVELS.items():
    ratio = T_max / val
    reached = "✅" if T_max >= val else "❌"
    print(f"  {name:6s} = {val:3.0f} μK  →  {reached}  max/ratio = {ratio:.3f}")

# 5. Check if any hot spot reaches F₆/F₇/F₈ levels
print(f"\n[5/5] Does ANY pixel reach Fibonacci levels?")
for name, val in F_LEVELS.items():
    above = T > val
    n_above = np.sum(above)
    if n_above > 0:
        # Find the brightest
        bright_idx = np.argmax(T * above)
        lb, bb = hp.pix2ang(nside, bright_idx, lonlat=True)
        print(f"  {name} = {val:3.0f} μK: {n_above:>8,} pixels above, brightest = {T[bright_idx]:+.1f} μK @ ({lb:.1f}°, {bb:.1f}°)")
    else:
        # Find closest approach
        deficit = val - T_max
        print(f"  {name} = {val:3.0f} μK: ❌ 0 pixels above. Closest approach = {T_max:+.1f} μK (deficit = {deficit:.0f} μK)")

# Also check: how many σ above the mean is the maximum?
mean_sky = np.mean(T)
std_sky = np.std(T)
print(f"\n  Sky mean = {mean_sky:+.1f} μK, sky std = {std_sky:.1f} μK")
print(f"  Max is {(T_max - mean_sky) / std_sky:.2f} σ above mean")

# Compare F_5 cold spot: cold spot is -124.6 μK at 5° smoothing
# The cold spot is ~2.95σ below mean
cold_spot_T = -124.6
print(f"  Cold spot is {(cold_spot_T - mean_sky) / std_sky:.2f} σ below mean")

# 5b. Galactic plane robustness check
print(f"\n[5b/5] Galactic plane mask robustness")
l_pix, b_pix = hp.pix2ang(nside, np.arange(len(T)), lonlat=True)
for mask_b in [20, 25, 30, 40, 50]:
    mask = np.abs(b_pix) >= mask_b
    T_m = T.copy()
    T_m[~mask] = -np.inf
    if np.any(T_m > -np.inf):
        mx = np.nanmax(T_m)
        mi = np.argmax(T_m)
        lm, bm = hp.pix2ang(nside, mi, lonlat=True)
        print(f"  |b|>={mask_b:2d}°:  max={mx:+7.1f} μK @ ({lm:7.2f}°, {bm:6.2f}°)  deficit to F₆ = {240-mx:.0f} μK")

# Save results
with open(os.path.join(OUTDIR, 'allsky_hotspots.txt'), 'w') as f:
    f.write(f"# All-sky hot spot search results\n")
    f.write(f"# Smoothing: {FWHM_DEG}° FWHM\n")
    f.write(f"T_global_max {T_max:.1f}\n")
    f.write(f"l_global_max {l_max:.2f}\n")
    f.write(f"b_global_max {b_max:.2f}\n")
    f.write(f"T_sky_mean {mean_sky:.1f}\n")
    f.write(f"T_sky_std {std_sky:.1f}\n")
    f.write(f"max_sigma {(T_max - mean_sky)/std_sky:.2f}\n")
    # Top 50 pixels
    f.write(f"# Top 50 pixels: rank, T_muK, l_deg, b_deg\n")
    for rank in range(50):
        pi = sorted_pix[rank]
        li, bi = hp.pix2ang(nside, pi, lonlat=True)
        f.write(f"{rank+1} {T[pi]:.1f} {li:.4f} {bi:.4f}\n")

print(f"\n✅ Saved: data/allsky_hotspots.txt")
print(f"{'='*60}")
print(f"O2 STEP 3 COMPLETE")
print(f"{'='*60}")