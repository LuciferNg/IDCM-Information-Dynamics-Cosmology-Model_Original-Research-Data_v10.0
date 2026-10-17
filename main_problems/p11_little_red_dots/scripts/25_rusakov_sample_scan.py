#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 closeout 攻堅 — 數據掃描 #3: Rusakov 樣本全光源系統峰距統計 (2026-10-17)
============================================================================
樣本 (Rusakov+2026 Nature 12 個 broad-line objects 中 9 個有 DJA 公開 G395M):
  A  JADES-GN-68797   z=5.0405  (已有 objA_g395m.fits)
  C  JADES-GN-73488   z=4.1325  (objC_g395m.fits) (+G395H objC_g395h.fits)
  E  RUBIES-EGS-49140 z=6.6852  (objE_g395m.fits)
  F  CEERS-EGS-1244   z=4.4779  (objF_g395m.fits)
  G  RUBIES-EGS-58237 z=3.6493  (已有 objG_g395m.fits)
  I  JADES-GN-53501   z=3.4304  (objI_g395m.fits)
  J  JADES-GN-38147   z=5.8683  (objJ_g395m.fits)
  K  RUBIES-EGS-50052 z=5.2394  (objK_g395m.fits)

目標 (T2 統計判別): 每個光源 Hα 外峰距 Δv — 分佈 vs IDCM 階梯量子
  Δv_ladder(ℓ,n) = n·cπ/(88·4^ℓ); 主要候選 ℓ=3 n=5 = 836.1 km/s (record 16 單點命中)
  若 IDCM 正確: 峰距應聚集喺階梯值 (唔係連續分佈)
對照: 電子散射模型預言連續指數翼 (冇離散峰距) — 離散聚集 = IDCM 判別信號

輸出: data/26_rusakov_sample_scan.json
"""
import json, numpy as np, os
from astropy.io import fits

FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')
C_KM = 2.99792458e5
LAM_HA = 0.65628

SAMPLE = [
    # (name, file, z, resolution)
    ("A_JADES-GN-68797",   "objA_g395m.fits", 5.0405, "G395M R~1000"),
    ("C_JADES-GN-73488",   "objC_g395m.fits", 4.1325, "G395M R~1000"),
    ("C_JADES-GN-73488_H", "objC_g395h.fits", 4.1325, "G395H R~2700"),
    ("E_RUBIES-EGS-49140", "objE_g395m.fits", 6.6852, "G395M R~1000"),
    ("F_CEERS-EGS-1244",   "objF_g395m.fits", 4.4779, "G395M R~1000"),
    ("G_RUBIES-EGS-58237", "objG_g395m.fits", 3.6493, "G395M R~1000"),
    ("I_JADES-GN-53501",   "objI_g395m.fits", 3.4304, "G395M R~1000"),
    ("J_JADES-GN-38147",   "objJ_g395m.fits", 5.8683, "G395M R~1000"),
    ("K_RUBIES-EGS-50052", "objK_g395m.fits", 5.2394, "G395M R~1000"),
]

def analyze(fn, z):
    """返回 (主峰數, 峰位[Δv], 最大峰距, 中點偏移)"""
    h = fits.open(os.path.join(FITS_DIR, fn))
    d = h[1].data
    w, f = d['wave'], d['flux']
    ok = ~np.isnan(f)
    cobs = LAM_HA*(1+z)
    mcont = ok & (((w>=cobs-0.10)&(w<=cobs-0.06)) | ((w>=cobs+0.06)&(w<=cobs+0.10)))
    if mcont.sum() < 8:
        return None
    A = np.polyfit(w[mcont], f[mcont], 1)
    m = ok & (w>=cobs-0.03) & (w<=cobs+0.03)
    wl, fl = w[m], f[m]-np.polyval(A, w[m])
    if len(wl) < 5:
        return None
    rms = np.nanstd(fl)
    # 峰搜尋: 平滑 3pt + 相對門檻 (寬線令絕對 σ 大, 用 0.1×max 同 script 24 一致)
    fs = np.convolve(fl, np.ones(3)/3, mode='same')
    fmax = np.nanmax(fs)
    peaks = []
    for i in range(1, len(fs)-1):
        if fs[i] > fs[i-1] and fs[i] > fs[i+1] and fs[i] > 0.10*fmax:
            peaks.append(float(wl[i]))
    # 合併 <200 km/s
    merged = []
    for p in peaks:
        if merged and C_KM*abs(p-merged[-1])/cobs < 200:
            continue
        merged.append(p)
    if len(merged) < 2:
        return {"n_peaks": len(merged), "peaks_dv": [C_KM*(p-cobs)/cobs for p in merged],
                "max_sep": None, "mid_off": None}
    dv = C_KM*abs(merged[-1]-merged[0])/cobs
    mid = (merged[-1]+merged[0])/2
    return {"n_peaks": len(merged), "peaks_dv": [C_KM*(p-cobs)/cobs for p in merged],
            "max_sep": dv, "mid_off": C_KM*(mid-cobs)/cobs}

# IDCM 階梯
def ladder(ell, n):
    return n*np.pi*C_KM/(88*4**ell)

LADDERS = [(ell, n, ladder(ell, n)) for ell in range(4) for n in range(1, 10)]

out = {"date": "2026-10-17", "sample_size": len(SAMPLE), "results": {}}
print(f"{'光源':<20} {'z':>7} {'峰數':>4} {'峰位 Δv (km/s)':>28} {'外峰距':>8} {'中點偏移':>8}")
print("-"*85)
seps = []
for name, fn, z, res in SAMPLE:
    r = analyze(fn, z)
    out["results"][name] = r
    if r is None:
        print(f"{name:<20} {z:>7.4f}  cont-fail")
        continue
    pk_str = ",".join(f"{v:+.0f}" for v in r["peaks_dv"]) or "-"
    sep = r["max_sep"]
    if sep:
        seps.append((name, sep, r["mid_off"]))
    print(f"{name:<20} {z:>7.4f} {r['n_peaks']:>4} {pk_str:>28} {sep if sep else '-':>8} {r['mid_off'] if r['mid_off'] is not None else '-':>8}")

# ---- 階梯距離統計 ----
print("\n" + "="*70)
print("外峰距 vs IDCM 階梯量子:")
print("="*70)
match_summary = []
for name, sep, off in seps:
    print(f"\n{name}: Δv = {sep:.0f} km/s (中點偏移 {off:+.0f})")
    best = []
    for ell, n, dv0 in LADDERS:
        r = sep/dv0
        if abs(r-round(r)) < 0.15 and r >= 0.5:
            best.append((ell, n, dv0, r))
    for ell, n, dv0, r in best:
        tag = "EXACT" if abs(r-round(r)) < 0.02 else "近"
        print(f"  → {r:.2f}× ℓ={ell} n={n} ({dv0:.0f} km/s) [{tag} dev {abs(r-round(r))*100:.1f}%]")
    if best:
        match_summary.append((name, sep, best))

# 判別: 幾多比例命中階梯?
n_meas = len(seps)
n_hit = len(match_summary)
print(f"\n測到外峰距: {n_meas}/{sum(1 for r in out['results'].values() if r)}")
print(f"階梯命中 (≥1 候選): {n_hit}/{n_meas}")
out["summary"] = {"measured": n_meas, "ladder_hit": n_hit}
if n_meas:
    out["summary"]["hit_fraction"] = n_hit/n_meas

with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data/26_rusakov_sample_scan.json', 'w') as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print("\n[INFO] 統計註: 電子散射模型預言連續指數翼 — 冇離散峰距聚集;")
print("       IDCM 預言峰距應聚集喺階梯值 (836.1/1672/3344/6688...)")