#!/usr/bin/env python3
"""
08_plot_results.py — O8 結果圖
================================
1. 冷斑徑向 profile (1.0° 平滑) + a/2π 標記
2. 半峰半徑 vs 平滑尺度 (σ² 外推圖)
"""
import healpy as hp
import numpy as np
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u

a_edge = 26.091346
pred = a_edge/(2*np.pi)

nodes = []
with open("/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
sc = SkyCoord(ra=nodes[:, 0]*u.deg, dec=nodes[:, 1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg

cache_dir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data/smooth_cache"
outdir = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o8_scale_radius/data"

# ===== 圖 1: 冷斑 profile (1.0° 平滑) =====
m = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth1.0.fits", field=0))
nside = hp.get_nside(m)
cv = hp.ang2vec(l_deg[0], b_deg[0], lonlat=True)
pix = hp.query_disc(nside, cv, np.radians(12))
pv = np.array(hp.pix2vec(nside, pix)).T
angs = np.degrees(np.arccos(np.clip(pv @ cv, -1, 1)))
vals = m[pix]
bins = np.linspace(0, 12, 121)
idx = np.digitize(angs, bins[1:-1])
prof = np.array([((bins[j]+bins[j+1])/2, np.mean(vals[idx==j])) for j in range(120) if (idx==j).sum() > 0])
r, v = prof[:, 0], prof[:, 1]

fig, ax = plt.subplots(1, 2, figsize=(14, 5))

ax[0].plot(r, v*1e6, 'b-', lw=2, label='冷斑 profile (1.0° 平滑)')
ax[0].axhline(0, color='k', ls='--', lw=0.8)
ax[0].axvline(pred, color='r', ls='--', lw=2, label=f'a/2π = {pred:.3f}°')
ax[0].axvline(180/44, color='g', ls=':', lw=1.5, label=f'180/44 = {180/44:.3f}°')
ax[0].axvline(4.17, color='orange', ls=':', lw=1.5, label='Vielva R8 = 4.17°')
# 半峰標記
T0 = v[0]
ax[0].axhline(T0*1e6/2, color='gray', ls='--', lw=1, label=f'半峰 = {T0*1e6/2:.0f} μK')
ax[0].set_xlabel('θ (°)')
ax[0].set_ylabel('T (μK)')
ax[0].set_title('冷斑徑向溫度 profile\n(平滑後凹陷半峰 ≈ 4.15° = a/2π)')
ax[0].legend(fontsize=8)
ax[0].grid(alpha=0.3)

# ===== 圖 2: σ² 外推 =====
scales = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
hwhms = []
for s in scales:
    ms = hp.remove_dipole(hp.read_map(f"{cache_dir}/smica2_smooth{s}.fits", field=0))
    ns = hp.get_nside(ms)
    pix = hp.query_disc(ns, cv, np.radians(15))
    pv2 = np.array(hp.pix2vec(ns, pix)).T
    angs2 = np.degrees(np.arccos(np.clip(pv2 @ cv, -1, 1)))
    vals2 = ms[pix]
    bins2 = np.linspace(0, 15, 75)
    idx2 = np.digitize(angs2, bins2[1:-1])
    prof2 = np.array([((bins2[j]+bins2[j+1])/2, np.mean(vals2[idx2==j])) for j in range(74) if (idx2==j).sum() > 0])
    r2, v2 = prof2[:, 0], prof2[:, 1]
    T02 = v2[0]
    tgt = T02/2
    hr = np.nan
    for j in range(1, len(v2)):
        if (v2[j]-tgt)*(v2[j-1]-tgt) <= 0:
            tt = (tgt - v2[j-1])/(v2[j]-v2[j-1])
            hr = r2[j-1] + tt*(r2[j]-r2[j-1])
            break
    hwhms.append(hr)
hwhms = np.array(hwhms)
sig2 = (np.array(scales)/(2*math.sqrt(2*math.log(2))))**2

mask = np.array(scales) <= 3.0
A = np.vstack([sig2[mask], np.ones(mask.sum())]).T
coef, *_ = np.linalg.lstsq(A, hwhms[mask]**2, rcond=None)
slope, intercept = coef
hwhm_true = math.sqrt(max(0, intercept))

x_fit = np.linspace(0, 4.5, 100)
y_fit = slope*x_fit + intercept

ax[1].plot(sig2, hwhms**2, 'bo', ms=6, label='實測 HWHM²')
ax[1].plot(x_fit, y_fit, 'r-', lw=2, label=f'σ² 外推 (0.5-3.0°)')
ax[1].axhline(intercept, color='r', ls='--', lw=1)
ax[1].axvline(0, color='k', lw=0.8)
ax[1].annotate(f'HWHM_true = √{intercept:.3f}\n= {hwhm_true:.3f}°\nvs a/2π = {pred:.3f}°\n偏差 {(hwhm_true-pred)/pred*100:.2f}%',
               xy=(0.15, intercept*1.15), fontsize=10, color='darkred')
ax[1].set_xlabel('σ²_smooth (deg²)')
ax[1].set_ylabel('HWHM² (deg²)')
ax[1].set_title('去平滑外推: HWHM² = HWHM_true² + σ²_smooth·2ln2\n(截距 = 真實結構半徑)')
ax[1].legend(fontsize=9)
ax[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f"{outdir}/o8_scale_closure.png", dpi=150)
print(f"✅ 已存: {outdir}/o8_scale_closure.png")
print(f"HWHM_true = {hwhm_true:.4f}° vs a/2π = {pred:.4f}° (偏差 {(hwhm_true-pred)/pred*100:.2f}%)")
