#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 全樣本 forward-model 掃描 (2026-10-17)
==================================================
判生死三條件②完整化: 全部 9 光源 × 可用光譜 (G395H/G395M/PRISM)
  M0: 單 Gaussian + cont
  M1: 自由雙 Gaussian + cont (峰距/振幅/σ 自由)
  M2: IDCM 嚴格對稱雙峰 + cont (同振幅/同σ, ±d)

輸出統一表: 每光源 Δv(M1), 峰高比, ΔAIC, 判定
兼測 T2: 峰距有冇離散聚集 (IDCM 階梯候選 ℓ=2/ℓ=3 n=1..5)
Caveats: G395M R~1000 峰距誤差大 (script 26 bias +3000) — 只做參考
"""
import json, numpy as np, os
from astropy.io import fits
from scipy.optimize import curve_fit

FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')
C_KM = 2.99792458e5
LAM = {'Hβ': 0.48614, 'Hα': 0.65628, 'Ha': 0.65628}

SAMPLE = [
    ("A_JADES-GN-68797",  "objA_g395h.fits", 5.0405, 2700, "Hα"),
    ("A_JADES-GN-68797_M","objA_g395m.fits", 5.0405, 1000, "Hα"),
    ("C_JADES-GN-73488",  "objC_g395h.fits", 4.1325, 2700, "Hα"),
    ("C_JADES-GN-73488_M","objC_g395m.fits", 4.1325, 1000, "Hα"),
    ("E_RUBIES-EGS-49140","objE_g395m.fits", 6.6852, 1000, "Hα"),
    ("F_CEERS-EGS-1244",  "objF_g395m.fits", 4.4779, 1000, "Hα"),
    ("G_RUBIES-EGS-58237","objG_g395m.fits", 3.6493, 1000, "Hα"),
    ("I_JADES-GN-53501",  "objI_g395m.fits", 3.4304, 1000, "Hα"),
    ("J_JADES-GN-38147",  "objJ_g395m.fits", 5.8683, 1000, "Hα"),
    ("K_RUBIES-EGS-50052","objK_g395m.fits", 5.2394, 1000, "Hα"),
]

# IDCM 階梯候選 (record 14 核心: ℓ=2 668.9, ℓ=3 n=1..5: 167.2,334.5,501.7,668.9,836.1)
LADDER = {'ℓ=2': 668.9, 'ℓ=3n1': 167.2, 'ℓ=3n2': 334.5, 'ℓ=3n3': 501.7,
          'ℓ=3n4': 668.9, 'ℓ=3n5': 836.1}

def load_line(fn, z, lname, w=0.03):
    h = fits.open(os.path.join(FITS_DIR, fn))
    d = h[1].data
    wv, f = d['wave'], d['flux']
    ok = ~np.isnan(f)
    cobs = LAM.get(lname, LAM['Hα'])*(1+z)
    mcont = ok & (((wv>=cobs-0.10)&(wv<=cobs-0.06)) | ((wv>=cobs+0.06)&(wv<=cobs+0.10)))
    if mcont.sum() < 6:
        return None
    A = np.polyfit(wv[mcont], f[mcont], 1)
    m = ok & (wv>=cobs-w) & (wv<=cobs+w)
    if m.sum() < 12:
        return None
    return wv[m]-cobs, f[m]-np.polyval(A, wv[m]), cobs

def m0(x, a, s, x0, c0):
    return a*np.exp(-0.5*((x-x0)/s)**2) + c0
def m1(x, a1, a2, s1, s2, p1, p2, c0):
    return a1*np.exp(-0.5*((x-p1)/s1)**2) + a2*np.exp(-0.5*((x-p2)/s2)**2) + c0
def m2(x, a, s, d, c0):
    return a*(np.exp(-0.5*((x-d)/s)**2) + np.exp(-0.5*((x+d)/s)**2)) + c0

def fit_res(model, x, y, p0):
    try:
        popt, _ = curve_fit(model, x, y, p0=p0, maxfev=30000)
        resid = y - model(x, *popt)
        n, k = len(y), len(popt)
        sig2 = np.var(resid, ddof=k)
        if sig2 <= 0:
            return None, None
        aic = n*np.log(sig2) + 2*k
        return popt, aic
    except Exception:
        return None, None

out = {"date": "2026-10-17", "ladders_km_s": LADDER, "results": {}}
print(f"{'光源':<20} {'R':>4} {'Δv':>6} {'峰高比R':>7} {'ΔAIC_M1':>8} {'ΔAIC_M2':>8} {'階梯命中':>10}")
print("="*92)
peak_seps = []
for name, fn, z, Rres, ln in SAMPLE:
    r = load_line(fn, z, ln)
    if r is None:
        print(f"{name:<20} cont fail")
        continue
    x, y, cobs = r
    # M0
    p0_m0 = [np.max(y), 0.002, 0.0, np.min(y)]
    popt0, a0 = fit_res(m0, x, y, p0_m0)
    # M1
    p0_m1 = [np.max(y)*0.6, np.max(y)*0.4, 0.0015, 0.0015, -0.002, 0.003, np.min(y)]
    popt1, a1 = fit_res(m1, x, y, p0_m1)
    # M2
    p0_m2 = [np.max(y)*0.8, 0.0012, 0.0030, np.min(y)]
    popt2, a2 = fit_res(m2, x, y, p0_m2)
    if popt0 is None or popt1 is None or popt2 is None:
        print(f"{name:<20} fit fail")
        continue
    # M1 峰距/峰高比
    dv1 = C_KM*abs(popt1[4]-popt1[5])/cobs
    i_bl = 0 if popt1[4] < popt1[5] else 1
    a_bl, a_rd = popt1[i_bl], popt1[1-i_bl]
    rr = a_bl/a_rd if a_rd > 0 else float('nan')
    peak_seps.append(dv1)
    # 階梯命中: |dv - ladder| / ladder < 0.12
    hit = ""
    for k, v in LADDER.items():
        if abs(dv1-v)/v < 0.12:
            hit = k
            break
    da1 = a1-a0 if a0 is not None else None
    da2 = a2-a0 if a0 is not None else None
    out["results"][name] = {"z": z, "R": Rres, "line": ln,
                            "dv_M1": float(dv1), "ratio": float(rr) if rr==rr else None,
                            "dAIC_M1_M0": float(da1) if da1 is not None else None,
                            "dAIC_M2_M0": float(da2) if da2 is not None else None,
                            "ladder_hit": hit or None, "N": len(x)}
    print(f"{name:<20} {Rres:>4} {dv1:6.0f} {rr:7.3f} "
          f"{da1 if da1 is not None else float('nan'):8.1f} "
          f"{da2 if da2 is not None else float('nan'):8.1f} {hit:>10}")

# T2 統計: 峰距分佈
print("\n" + "="*92)
if peak_seps:
    arr = np.array(peak_seps)
    print(f"T2 峰距分佈: {arr} km/s")
    print(f"  mean={arr.mean():.0f}, std={arr.std():.0f}, min={arr.min():.0f}, max={arr.max():.0f}")
    # 離散性: GMM/聚集測試 — 簡單: 有冇任何兩個峰距相近 (同階梯?)
    from itertools import combinations
    close = [(i, j, abs(peak_seps[i]-peak_seps[j]))
             for i, j in combinations(range(len(peak_seps)), 2)]
    close = sorted(close, key=lambda t: t[2])[:3]
    print(f"  最近三對: {[f'{peak_seps[a]:.0f}~{peak_seps[b]:.0f} ({d:.0f})' for a,b,d in close]}")
    out["summary"] = {"n_fit": len(peak_seps), "seps": [float(v) for v in peak_seps],
                      "mean": float(arr.mean()), "std": float(arr.std())}

with open(os.path.join(os.path.dirname(__file__), '..', 'data', '29_full_sample_m1.json'), 'w') as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print("\n[寫入] data/29_full_sample_m1.json")