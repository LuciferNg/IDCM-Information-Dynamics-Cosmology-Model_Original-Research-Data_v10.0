#!/usr/bin/env python3
"""
O42 新線 C3 — 冷斑本徵尺度 fit (fit σ 令高斯模型匹配超額譜)
=============================================================
發現: 高斯 dip σ=1.77° (4.17°FWHM) 低估冷斑 SMHW 超額響應 4-5 倍。
原因: 4.17° 平滑只係量度工具, 冷斑本徵尺度更大 (Vielva 2004: ~10°)。

做法: fit 高斯 dip 嘅 σ (本徵尺度), 令模型 SMHW 超額譜匹配實測超額譜。
      A 固定 134.2 μK (O41 閉合), 只 fit σ。
"""
import os, json
import numpy as np
import healpy as hp
from scipy.special import eval_legendre
from scipy.optimize import minimize_scalar

OUTDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
A = 134.2
NSIDE = 1024
LMAX = 3*NSIDE
# 冷斑中心
v0 = hp.ang2vec(209, -57, lonlat=True)

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

# 實測超額譜 (09b)
R_list = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0]
w_excess = np.array([-14.40, -24.97, -29.36, -31.08, -29.85, -23.46, -11.19])

npix = hp.nside2npix(NSIDE)
pix = np.arange(npix)
v = hp.pix2vec(NSIDE, pix)
ang = np.degrees(np.arccos(np.clip(v[0]*v0[0]+v[1]*v0[1]+v[2]*v0[2], -1, 1)))
pix0 = np.argmin(ang)

# 預計算 wl for all R
wls = {R: smhw_wl(np.radians(R), LMAX) for R in R_list}

def model_spectrum(sigma_deg):
    """高斯 dip σ 嘅 SMHW 係數喺中心"""
    model = -A * np.exp(-ang**2/(2*sigma_deg**2)) * 1e-6  # K
    a_lm = hp.map2alm(model, lmax=LMAX)
    out = []
    for R in R_list:
        wl = wls[R]
        alm_w = hp.almxfl(a_lm, wl)
        wmap = hp.alm2map(alm_w, nside=NSIDE, lmax=LMAX)
        alm_lo = hp.almxfl(a_lm, wl * (np.arange(LMAX+1) < 3))
        wmap -= hp.alm2map(alm_lo, nside=NSIDE, lmax=LMAX)
        out.append(float(wmap[pix0]) * 1e6)
    return np.array(out)

def chi2(sigma):
    pred = model_spectrum(sigma)
    return np.sum((pred - w_excess)**2 / w_excess**2)

# 掃描 σ 0.5-8°
sigmas = np.linspace(0.5, 8.0, 16)
print(f"{'σ(°)':>6} {'χ²':>10}")
best_s, best_c = None, 1e9
for s in sigmas:
    c = chi2(s)
    print(f"{s:>6.2f} {c:>10.1f}")
    if c < best_c:
        best_c, best_s = c, s

# 精細 fit
res = minimize_scalar(chi2, bounds=(0.5, 8.0), method='bounded')
print(f"\n最佳 σ = {res.x:.2f}° (χ²={res.fun:.1f})")
pred_best = model_spectrum(res.x)
print(f"\n{'R(°)':>6} {'超額':>10} {'模型(σ={:.1f})'.format(res.x):>14} {'比率':>8}")
for R, e, p in zip(R_list, w_excess, pred_best):
    print(f"{R:>6.2f} {e:>10.2f} {p:>14.2f} {p/e:>8.2f}")

# 詮釋
print(f"\n冷斑本徵尺度 σ = {res.x:.2f}° → FWHM = {res.x*2.355:.2f}°")
print(f"文獻: Vielva 2004 angular radius ~5°, Planck 2013 ~10° 直徑")
print(f"IDCM: R8 = 4.17° (O5 結構尺度), A₅ 節點間距 26.17°")
