#!/usr/bin/env python3
"""
O45 — 閉合攻堅 3: Super-Gaussian 輪廓閉合 (2026-09-12)
========================================================
模型: T(θ) = -A·exp(-(θ/σ)ⁿ/2)   (A=134.2 固定)
  n=2  → 高斯 (已證實唔夠: σ_T=205° vs σ_w=5.75°)
  n>2  → 頂帽狀 (flat-top core + sharp edge)

目標: 掃 (σ, n) 搵同時 match 兩個實測通道:
  T_pix(4.17° smooth) = -134.19 μK
  w_SMHW(R=4.17°)     = -31.17 μK
若存在唯一 (σ*, n*) → 冷斑輪廓細節結構性閉合 (非高斯性量化)
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre

PROJECT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

A_IDCM = 134.2
COLD = (209.0, -57.0)
NSIDE = 512          # nside=512 已夠 (pixel ~0.11° << R=4.17°), 快 ~8 倍
LMAX = 3*NSIDE       # 1536

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

npix = hp.nside2npix(NSIDE)
v0 = hp.ang2vec(COLD[0], COLD[1], lonlat=True)
v = hp.pix2vec(NSIDE, np.arange(npix))
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))
pix0 = hp.ang2pix(NSIDE, COLD[0], COLD[1], lonlat=True)

T_pix_obs = -134.19
w_obs = -31.17

wl_417 = smhw_wl(np.radians(4.17), LMAX)

def super_gauss(theta_deg, sigma, n):
    """T(θ) = -A·exp(-(θ/σ)ⁿ/2)"""
    return -A_IDCM * np.exp(-(theta_deg/sigma)**n / 2)

print(f"{'σ(°)':>6} {'n':>4} {'T_pix(μK)':>10} {'w4.17(μK)':>10} {'χ²':>8}")
print("-" * 46)

best = None
results = []
sigma_grid = np.arange(2.0, 12.01, 0.5)
n_grid = [2, 3, 4, 5, 6, 8, 10, 12]

for sigma in sigma_grid:
    for n in n_grid:
        m = super_gauss(ang, sigma, n) * 1e-6  # K
        m_sm = hp.smoothing(m, fwhm=np.radians(4.17))
        T_pix = float(m_sm[pix0]) * 1e6
        
        a = hp.map2alm(m, lmax=LMAX)
        aw = hp.almxfl(a, wl_417)
        wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
        alo = hp.almxfl(a, wl_417 * (np.arange(LMAX+1) < 3))
        wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
        w = float(wm[pix0]) * 1e6
        
        # χ² = (ΔT/0.5)² + (Δw/0.3)²  (實測誤差約 0.5 μK pixel, 0.3 μK wavelet)
        chi2 = ((T_pix - T_pix_obs)/0.5)**2 + ((w - w_obs)/0.3)**2
        results.append({'sigma': float(sigma), 'n': int(n), 'T_pix': T_pix, 'w': w, 'chi2': chi2})
        
        if chi2 < 5:  # 只有接近嘅先 print
            print(f"{sigma:>6.1f} {n:>4d} {T_pix:>10.2f} {w:>10.2f} {chi2:>8.2f}")

# 最優匹配
results.sort(key=lambda r: r['chi2'])
print("\n最優 5 個 (σ, n):")
for r in results[:5]:
    print(f"  σ={r['sigma']:.1f}°, n={r['n']}, T_pix={r['T_pix']:.2f} (obs {T_pix_obs}), "
          f"w={r['w']:.2f} (obs {w_obs}), χ²={r['chi2']:.3f}")

# 高精度精修: 圍繞最優解細掃
print("\n高精度精修 (圍繞最優解):")
r0 = results[0]
sig_fine = np.arange(max(2.0, r0['sigma']-1.0), min(12.0, r0['sigma']+1.0)+0.01, 0.1)
n_fine = np.arange(max(2, r0['n']-2), r0['n']+3)

best2 = None
for sigma in sig_fine:
    for n in n_fine:
        m = super_gauss(ang, sigma, n) * 1e-6
        m_sm = hp.smoothing(m, fwhm=np.radians(4.17))
        T_pix = float(m_sm[pix0]) * 1e6
        a = hp.map2alm(m, lmax=LMAX)
        aw = hp.almxfl(a, wl_417)
        wm = hp.alm2map(aw, nside=NSIDE, lmax=LMAX)
        alo = hp.almxfl(a, wl_417 * (np.arange(LMAX+1) < 3))
        wm -= hp.alm2map(alo, nside=NSIDE, lmax=LMAX)
        w = float(wm[pix0]) * 1e6
        chi2 = ((T_pix - T_pix_obs)/0.5)**2 + ((w - w_obs)/0.3)**2
        if best2 is None or chi2 < best2['chi2']:
            best2 = {'sigma': sigma, 'n': int(n), 'T_pix': T_pix, 'w': w, 'chi2': chi2}

print(f"  ★ 最優: σ*={best2['sigma']:.2f}°, n*={best2['n']}")
print(f"    T_pix = {best2['T_pix']:.2f} μK (obs {T_pix_obs}), Δ={abs(best2['T_pix']-T_pix_obs):.2f}")
print(f"    w     = {best2['w']:.2f} μK (obs {w_obs}), Δ={abs(best2['w']-w_obs):.2f}")
print(f"    χ² = {best2['chi2']:.3f}")

# ---------- 儲存 ----------
out = {
    'product': 'O45 closure-3: super-Gaussian profile closure',
    'date': '2026-09-12',
    'model': 'T(θ) = -A·exp(-(θ/σ)ⁿ/2), A=134.2 fixed',
    'observables': {'T_pix': T_pix_obs, 'w_R4.17': w_obs},
    'best': best2,
    'grid_results': results,
    'conclusion': (
        "若 χ²<2 有唯一 (σ*,n*) → 冷斑輪廓 = super-Gaussian (n*>2 頂帽狀) 同時閉合 "
        "pixel 同 SMHW 兩通道; n* 量化非高斯性, 解釋 1.4× 偏差"
    )
}
with open(os.path.join(OUTDIR, '05_supergauss_closure.json'), 'w') as f:
    json.dump(out, f, indent=2)
print(f"\n儲存: {OUTDIR}/05_supergauss_closure.json")