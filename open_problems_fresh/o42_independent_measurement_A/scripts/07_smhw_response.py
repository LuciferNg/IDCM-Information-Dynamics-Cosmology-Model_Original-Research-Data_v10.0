#!/usr/bin/env python3
"""
O42 延伸 A3 — SMHW 響應閉合 (harmonic 空間, 同 01 完全 parallel)
=================================================================
模型: 高斯 dip ΔT(θ) = −A·exp(−θ²/2σ²), A=134.2 μK, σ = 4.17°FWHM/2.355
(呢個係「平滑後冷斑」嘅 profile 近似)

步驟 (同 01 完全一致):
  1. 模型 map → map2alm (lmax=3072)
  2. SMHW w_l(R) 應用 (almxfl)
  3. 扣 l<3 (無偏)
  4. 抽中心 → 預言 SMHW 係數

比較: 預言 vs 實測 −31.17 μK (R=4.17°)
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre

OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NSIDE = 1024
LMAX = 3*NSIDE

A = 134.2
sigma_deg = 4.17/2.355

def smhw_wl(R_rad, lmax, npts=200):
    gamma, wgt = np.polynomial.legendre.leggauss(npts)
    gamma = (gamma+1)*np.pi/2; wgt = wgt*np.pi/2
    x = gamma/(2*R_rad)
    psi = (2*np.pi)**(-0.5)/R_rad*(1+x**2)*(2-x**2)*np.exp(-gamma**2/(2*R_rad**2))
    cg = np.cos(gamma); ls = np.arange(lmax+1)
    wl = np.empty(lmax+1)
    for l in ls:
        wl[l] = 2*np.pi*np.sum(wgt*psi*eval_legendre(l,cg)*np.sin(gamma))
    return wl

# 1. 模型 map: 高斯 dip 喺 (209,-57)
npix = hp.nside2npix(NSIDE)
v0 = hp.ang2vec(209, -57, lonlat=True)
pix = np.arange(npix)
v = hp.pix2vec(NSIDE, pix)
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))
model = -A * np.exp(-ang**2 / (2*sigma_deg**2))  # μK
model_K = model * 1e-6  # 轉 K (同 01 raw 一致)
print(f"模型: 高斯 dip A={A} μK σ={sigma_deg:.3f}°, 中心 {model_K[np.argmin(ang)]*1e6:.1f} μK")

# 2. harmonic + SMHW
a_lm = hp.map2alm(model_K, lmax=LMAX)
sj = json.load(open(os.path.join(OUTDIR, '01_smhw_results.json')))
print(f"\n{'R(°)':>6} {'模型SMHW(μK)':>14} {'實測SMHW(μK)':>14} {'比率':>8} {'吻合?':>6}")
print("-" * 54)
ok = 0
for R in [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]:
    wl = smhw_wl(np.radians(R), LMAX)
    alm_w = hp.almxfl(a_lm, wl)
    wmap = hp.alm2map(alm_w, nside=NSIDE, lmax=LMAX)
    alm_lo = hp.almxfl(a_lm, wl * (np.arange(LMAX+1) < 3))
    wmap -= hp.alm2map(alm_lo, nside=NSIDE, lmax=LMAX)
    pred = float(wmap[np.argmin(ang)]) * 1e6
    obs = sj['smhw'][str(R)]['T']
    ratio = pred/obs if obs != 0 else np.nan
    good = abs(ratio-1) < 0.35
    ok += good
    print(f"{R:>6.2f} {pred:>14.2f} {obs:>14.2f} {ratio:>8.3f} {'✅' if good else ''}")

print(f"\n吻合率: {ok}/7")
