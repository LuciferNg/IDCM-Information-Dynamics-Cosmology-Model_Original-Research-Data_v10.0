#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 矯正版 T1 終判: M6 = IDCM 對稱雙峰 × absorber dip (2026-10-17)
==========================================================================
A (R~2700) 舊 T1 (record 20: Δv(Hβ)/Δv(Hα)=1.68) 受到 absorber 污染:
A Hα 有 absorber (script 30: depth 0.98, dv=−283 km/s, ΔAIC −97),
A Hβ 冇 (+4.3).

矯正判別: 邊個模型 fit 得最好?
  M0: 單 Gaussian + cont (歷史基準)
  M4: broad Gaussian × (1−dip) + cont (單 broad + absorber)
  M6: IDCM 對稱雙峰 × (1−dip) + cont (模態對 + absorber) ← T1 修正版
  M1: 自由雙 Gaussian + cont (無 absorber)

若 M6 好過 M4 ⟹ 對稱模態對喺 absorber 修正後存在 (IDCM 復活)
若 M4 ≥ M6 ⟹ 即使加 absorber, 對稱雙峰都唔支持 (IDCM 仍然拒)
"""
import numpy as np, os
from astropy.io import fits
from scipy.optimize import curve_fit

FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')
C_KM = 2.99792458e5
LAM = {'Hα': 0.65628, 'Hβ': 0.48614}

def load_win(fn, z, lname, w=0.04):
    h = fits.open(os.path.join(FITS_DIR, fn))
    d = h[1].data
    wv, f = d['wave'], d['flux']
    ok = ~np.isnan(f)
    cobs = LAM[lname]*(1+z)
    mcont = ok & (((wv>=cobs-0.12)&(wv<=cobs-0.07)) | ((wv>=cobs+0.07)&(wv<=cobs+0.12)))
    A = np.polyfit(wv[mcont], f[mcont], 1)
    m = ok & (wv>=cobs-w) & (wv<=cobs+w)
    return wv[m]-cobs, f[m]-np.polyval(A, wv[m]), cobs

def m0(x, a, s, x0, c0):
    return a*np.exp(-0.5*((x-x0)/s)**2) + c0

def m4(x, a_b, s_b, x0, a_a, s_a, dv_km, c0):
    v = C_KM*(x-x0)/cobs
    dip = 1.0 - a_a*np.exp(-0.5*((v-dv_km)/s_a)**2)
    return a_b*np.exp(-0.5*(v/s_b)**2)*dip + c0

def m6(x, a_t, s_t, d_km, a_a, s_a, dv_km, c0):
    """IDCM 對稱雙峰 (±d_km/2) × absorber dip"""
    v = C_KM*x/cobs
    peak = np.exp(-0.5*((v-d_km/2)/s_t)**2) + np.exp(-0.5*((v+d_km/2)/s_t)**2)
    dip = 1.0 - a_a*np.exp(-0.5*((v-dv_km)/s_a)**2)
    return a_t*peak*dip + c0

def m1(x, a1, a2, s1, s2, p1, p2, c0):
    return a1*np.exp(-0.5*((x-p1)/s1)**2) + a2*np.exp(-0.5*((x-p2)/s2)**2) + c0

def fit_b(model, x, y, p0, bounds=(-np.inf, np.inf)):
    try:
        popt, _ = curve_fit(model, x, y, p0=p0, bounds=bounds, maxfev=100000)
        resid = y - model(x, *popt)
        n, k = len(y), len(popt)
        sig2 = np.var(resid, ddof=k)
        aic = n*np.log(sig2) + 2*k
        return popt, aic
    except Exception:
        return None, None

print("="*84)
print("A (JADES-GN-68797) R~2700 — 矯正版 T1: 模型比較 (M0/M4/M6/M1)")
print("="*84)
for lname in ['Hβ', 'Hα']:
    x, y, cobs = load_win('objA_g395h.fits', 5.0405, lname)
    ymax = y.max()
    # M0
    p0m, a0 = fit_b(m0, x, y, [0.9*ymax, 0.003, 0.0, y.min()])
    # M4 (single broad + dip)
    lo4 = [0, 100, -0.005, 0, 20, -800, -1e6]; hi4 = [2*ymax, 3000, 0.005, 1.5, 800, 800, 1e6]
    p4, a4 = fit_b(m4, x, y, [0.9*ymax, 1000, 0.0, 0.5, 200, -300, y.min()], (lo4, hi4))
    # M6 (对称双峰 + dip) — IDCM 阶梯度 d_km in [100, 2500]
    lo6 = [0, 10, 100, 0, 20, -800, -1e6]; hi6 = [2*ymax, 800, 2500, 1.5, 800, 800, 1e6]
    p6, a6 = fit_b(m6, x, y, [0.8*ymax, 150, 800, 0.4, 200, -300, y.min()], (lo6, hi6))
    # M1 (free double)
    p1, a1 = fit_b(m1, x, y, [0.5*ymax, 0.4*ymax, 0.0015, 0.0015, -0.002, 0.003, y.min()])
    print(f"\n{lname} (obs={cobs:.3f}, N={len(x)}):")
    print(f"  M0 單峰:         AIC={a0:.1f}  (基準)")
    if p4 is not None:
        print(f"  M4 單broad+dip:  AIC={a4:.1f}  ΔAIC={a4-a0:+.1f}   (σ_b={p4[1]:.0f}km/s, "
              f"dip={p4[3]:.2f}@{p4[5]:+.0f}km/s σ={p4[4]:.0f})")
    if p6 is not None:
        print(f"  M6 IDCM對稱+dip: AIC={a6:.1f}  ΔAIC={a6-a0:+.1f}   (峰距={p6[2]:.0f}km/s, "
              f"dip={p6[4]:.2f}@{p6[5]:+.0f}km/s σ={p6[3]:.0f}, 半寬={p6[1]:.0f}km/s)")
    if p1 is not None:
        print(f"  M1 自由雙峰:     AIC={a1:.1f}  ΔAIC={a1-a0:+.1f}   (Δv={C_KM*abs(p1[4]-p1[5])/cobs:.0f}km/s)")
    if p4 is not None and p6 is not None:
        verdict = "M6 勝 ⟹ 對稱模態對在吸收修正後存在 (IDCM 復活)" if a6 < a4 - 5 else \
                  ("M4 勝 ⟹ 即使加吸收, 對稱雙峰都唔支持" if a4 < a6 - 5 else "打和/無分別")
        print(f"  ⟹ {verdict} (ΔAIC M6−M4 = {a6-a4:+.1f})")

print("\n[注] E 驗證 (script 30): Hα absorber ΔAIC −65.8 (paper 確認 self-absorption)")
print("[注] IDCM 階梯: ℓ=3n1 167 / n2 334 / n3 502 / n4 669 / ℓ=2 669 / n5 836 km/s")