#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 矯正版 T1: absorber 移除後殘餘雙峰判別 (2026-10-17)
================================================================
Nikopoulos+2026 (A&A 710, A136) 官方: E (RUBIES-EGS-49140) 有 self-absorption —
Hα absorber FWHM≈350 km/s redshifted +47 km/s, Hβ FWHM≈520 km/s blueshifted −79,
食走 broad flux 10%/21%. 吸收深度隨波長減短而增.

⟹ 舊 T1 (record 20: A Δv(Hβ)/Δv(Hα)=1.68) 測嘅係「emission peak + absorption dip」
混合, 唔係真峰距. 矯正: 先 fit absorber, 移除後再量殘餘雙峰.

Part A: E 驗證 — 我哋 pipeline 可唔可以重現 paper 嘅 absorber 參數
Part B: A (R~2700) fit absorber (位置 free) + broad emission
Part C: A 殘餘 → M0/M1/M2 比較, 攞矯正後峰距, T1 ratio
"""
import json, numpy as np, os
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
    if mcont.sum() < 8:
        return None
    A = np.polyfit(wv[mcont], f[mcont], 1)
    m = ok & (wv>=cobs-w) & (wv<=cobs+w)
    if m.sum() < 15:
        return None
    return wv[m]-cobs, f[m]-np.polyval(A, wv[m]), cobs

# ---- 模型族 ----
# M4: broad Gaussian × (1 − absorption dip) + cont
#     emission: a_b, σ_b, x0 (broad centroid)
#     absorber: a_a (深度 0..1), σ_a, v_a (km/s, 相對 broad)
def m4_fix(x, a_b, s_b, x0, a_a, s_a, dv_km, c0):
    v = C_KM*(x-x0)/cobs          # km/s 相對 broad centroid
    vabs = v - dv_km              # absorber 位置 (km/s)
    dip = 1.0 - a_a*np.exp(-0.5*(vabs/s_a)**2)
    return a_b*np.exp(-0.5*((v)/(s_b))**2)*dip + c0

# M5: IDCM 對稱雙峰 × (1 − dip) + cont — 殘餘檢驗用 (M1 已經 free, M2 對稱)
def m1(x, a1, a2, s1, s2, p1, p2, c0):
    return a1*np.exp(-0.5*((x-p1)/s1)**2) + a2*np.exp(-0.5*((x-p2)/s2)**2) + c0
def m2(x, a, s, d, c0):
    return a*(np.exp(-0.5*((x-d)/s)**2) + np.exp(-0.5*((x+d)/s)**2)) + c0

def m0(x, a, s, x0, c0):
    return a*np.exp(-0.5*((x-x0)/s)**2) + c0

def fit_b(model, x, y, p0, bounds=(-np.inf, np.inf)):
    try:
        popt, _ = curve_fit(model, x, y, p0=p0, bounds=bounds, maxfev=100000)
        resid = y - model(x, *popt)
        n, k = len(y), len(popt)
        sig2 = np.var(resid, ddof=k)
        aic = n*np.log(sig2) + 2*k
        return popt, aic
    except Exception as e:
        return None, None

def aic_print(tag, a0, a1, a2=None, note=""):
    pass

out = {"date": "2026-10-17", "source": "Nikopoulos+2026 A&A 710 A136", "results": {}}

print("="*80)
print("Part A: E (RUBIES-EGS-49140) absorber 驗證 (paper: Hα +47/350, Hβ −79/520)")
print("="*80)
for lname in ['Hα', 'Hβ']:
    r = load_win('objE_g395m.fits', 6.6847, lname, w=0.05)
    if r is None:
        print(f"E {lname}: cont fail"); continue
    x, y, cobs = r
    # 初始: 粗略 broad 單峰
    popt_b, aic_b = fit_b(m0, x, y, [y.max()*0.9, 0.003, 0.0, y.min()])
    # M4: broad + absorber — σ 全部 km/s (v 已轉 km/s)
    p0 = [y.max()*0.9, 1500.0, 0.0, 0.5, 150.0, 47.0 if lname=='Hα' else -79.0, y.min()]
    # bounds: a_b(0,2max) s_b(50,20000) x0(-0.005,0.005) a_a(0,1.5) s_a(20,2000) dv_abs(-500,500) c0(-inf,inf)
    lo = [0, 50, -0.005, 0, 20, -500, -1e6]
    hi = [2*y.max(), 20000, 0.005, 1.5, 2000, 500, 1e6]
    popt_a, aic_a = fit_b(m4_fix, x, y, p0, (lo, hi))
    if popt_a is not None and popt_b is not None and aic_b is not None:
        print(f"E {lname}: M4 broad_amp={popt_a[0]:.1f} σ_b={popt_a[1]:.0f}km/s " 
              f"abs_depth={popt_a[3]:.3f} σ_a={popt_a[4]:.0f}km/s dv_abs={popt_a[5]:+.0f} km/s")
        print(f"  ΔAIC (M4 vs M0) = {aic_a - aic_b:+.1f}")
        print(f"  paper 預期: Hα +47 km/s / Hβ −79 km/s")
        out["results"][f"E_{lname}"] = {"abs_depth": float(popt_a[3]),
            "abs_dv_km_s": float(popt_a[5]), "dAIC_vs_M1": float(aic_a-aic_b)}
    else:
        print(f"E {lname}: M4 fit fail")

print("\n" + "="*80)
print("Part B: A (JADES-GN-68797, R~2700) absorber + 殘餘雙峰")
print("="*80)
for lname in ['Hβ', 'Hα']:
    r = load_win('objA_g395h.fits', 5.0405, lname, w=0.04)
    if r is None:
        print(f"A {lname}: cont fail"); continue
    x, y, cobs = r
    # M1 (自由雙峰) baseline
    p0m, a0m = fit_b(m0, x, y, [y.max()*0.9, 0.003, 0.0, y.min()])
    p1, a1 = fit_b(m1, x, y, [y.max()*0.6, y.max()*0.4, 0.0015, 0.0015, -0.002, 0.003, y.min()])
    # M4 (broad + absorber) — σ km/s, bounded
    lo4 = [0, 50, -0.005, 0, 20, -500, -1e6]
    hi4 = [2*y.max(), 20000, 0.005, 1.5, 2000, 500, 1e6]
    p4, a4 = fit_b(m4_fix, x, y, [y.max()*0.9, 1500.0, 0.0, 0.4, 150.0, 0.0, y.min()], (lo4, hi4))
    if p1 is None or p4 is None:
        print(f"A {lname}: fit fail"); continue
    print(f"\nA {lname} (obs={cobs:.3f}, N={len(x)}):")
    print(f"  M1: Δv={C_KM*abs(p1[4]-p1[5])/cobs:.0f} km/s, AIC={a1:.1f}")
    print(f"  M4: broad σ_b={p4[1]:.0f}km/s, abs_depth={p4[3]:.3f}, "
          f"σ_a={p4[4]:.0f}km/s, dv_abs={p4[5]:+.0f} km/s, AIC={a4:.1f}")
    print(f"  ΔAIC (M4 − M0) = {a4-a0m:+.1f}  {'absorber 較好' if a4<a0m else '無 absorber 跡象'}")
    # Part C: 殘餘 = y − broad emission (淨返 dip 結構)
    resid = y - (p4[0]*np.exp(-0.5*((C_KM*(x-p4[2])/cobs)/p4[1])**2) + p4[6])
    out["results"][f"A_{lname}"] = {
        "M1_dv_km_s": float(C_KM*abs(p1[4]-p1[5])/cobs),
        "M4_abs_depth": float(p4[3]), "M4_abs_dv_km_s": float(p4[5]),
        "M4_abs_sigma_km_s": float(C_KM*p4[4]/cobs),
        "dAIC_M4_M1": float(a4-a1)}

with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data/30_absorber_t1.json', 'w') as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print("\n[寫入] data/30_absorber_t1.json")