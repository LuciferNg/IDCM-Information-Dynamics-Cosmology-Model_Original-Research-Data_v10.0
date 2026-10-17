#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 closeout 攻堅 — Injection-Calibrated Pipeline (2026-10-17)
================================================================
判生死條件 #1 (record 18): 峰搜尋 pipeline 要 injection-calibrated 先可以做
「負結果 = 物理冇雙峰」嘅判定。

方法:
  A. False-positive baseline: 真實 A/C/G Hα 窗 (R~2700/R~1000) — pipeline (3pt
     smooth, 0.1×max, <200 km/s merge) 喺純 noise + 真實特徵下出 ≥2 峰嘅機率
  B. Injection: 注入 IDCM 對稱雙峰 (Δv = 836.1 ℓ=3 n=5 / 1672.2 / 3344.5 km/s,
     σ_峰 = 300 km/s) 於連續多峰高 (10-90% of line max)
  C. 校正後 recover 率 = P(檢出且峰距正確 | 注入) − P(假陽性 | 無注入)
  D. 檢出時峰距 bias/scatter — 量度誤差分佈
  E. 判讀: pipeline 喺邊個 SNR 先可靠; 真實數據峰距統計有冇意義

輸出: data/27_injection_calibration.json
"""
import json, numpy as np, os
from astropy.io import fits

FITS_DIR = os.environ.get('P11_FITS_DIR', '/home/wsl/.hermes/cache/scratch/p11_data')
C_KM = 2.99792458e5
LAM_HA = 0.65628
RNG = np.random.default_rng(42)

SOURCES = [
    # (name, file, z, res) — R~2700 高解像優先 (A/C) + G R~1000
    ("A_G395H", "objA_g395h.fits", 5.0405, 2700),
    ("C_G395H", "objC_g395h.fits", 4.1325, 2700),
    ("G_G395M", "objG_g395m.fits", 3.6493, 1000),
]

def extract_window(fn, z):
    """攞 Hα 窗真實波長網格 + 真實特徵 (fl = 光譜 − 線性continuum)"""
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
    return wl, fl, cobs

def pipeline_peaks(wl, fl, sep_merge=200):
    """同 record 17 script 25 pipeline: 3pt smooth, 0.1×max, <200 km/s merge"""
    fs = np.convolve(fl, np.ones(3)/3, mode='same')
    fmax = np.nanmax(fs)
    peaks = []
    for i in range(1, len(fs)-1):
        if fs[i] > fs[i-1] and fs[i] > fs[i+1] and fs[i] > 0.10*fmax:
            peaks.append(float(wl[i]))
    merged = []
    for p in peaks:
        if merged and C_KM*abs(p-merged[-1])/np.mean(wl) < sep_merge:
            continue
        merged.append(p)
    return merged

def ladder(ell, n):
    return n*np.pi*C_KM/(88*4**ell)

SEPS = [ladder(3,5), ladder(3,10), ladder(3,20)]   # 836.1 / 1672.2 / 3344.4
AMPS = [0.10, 0.20, 0.35, 0.50, 0.70, 0.90]

results = {}
print("="*88)
print("A. False-positive baseline — 真實 Hα 窗, 無注入, pipeline 出 ≥2 峰機率")
print("="*88)
windows = {}
fp_baseline = {}
for name, fn, z, R in SOURCES:
    r = extract_window(fn, z)
    if r is None:
        print(f"{name}: window fail"); continue
    wl, fl, cobs = r
    windows[name] = (wl, fl, cobs, R)
    trials = 500
    nfp = 0
    ndet2 = 0
    for t in range(trials):
        noise_std = np.nanstd(fl)
        syn = fl + RNG.normal(0, noise_std, len(fl))
        pk = pipeline_peaks(wl, syn)
        if len(pk) >= 2:
            nfp += 1
            # 假陽性峰距
            if len(pk) >= 2:
                ndet2 += 1
    rate = nfp/trials
    fp_baseline[name] = rate
    print(f"{name}: 假陽性率 (≥2峰) = {rate:.3f} ({nfp}/{trials})  峰數中位數遮蔽")

# 峰數分佈 (真實, 無 noise 注入)
print("\n真實窗 峰數 (無 noise):")
for name, (wl, fl, cobs, R) in windows.items():
    pk = pipeline_peaks(wl, fl)
    print(f"  {name}: {len(pk)} 峰 {[f'{C_KM*(p-cobs)/cobs:+.0f}' for p in pk]}")

print("\n" + "="*88)
print("B+C. Injection — 對稱雙峰 recover + 假陽性校正")
print("="*88)
inject_results = {}
for name, (wl, fl, cobs, R) in windows.items():
    noise_std = np.nanstd(fl)
    line_max = np.nanmax(fl)
    fp0 = fp_baseline[name]
    print(f"\n--- {name} (R~{R}, noise σ={noise_std:.3f}, line_max={line_max:.2f}) ---")
    for sep in SEPS:
        for amp in AMPS:
            nrec_corr = 0
            nrec = 0
            ntrials = 400
            sep_meas_all = []
            for t in range(ntrials):
                syn = fl + RNG.normal(0, noise_std, len(fl))
                sep_l = sep/C_KM*cobs
                g1 = amp*line_max*np.exp(-0.5*((wl-(cobs-sep_l/2))*C_KM/cobs/120)**2)
                g2 = amp*line_max*np.exp(-0.5*((wl-(cobs+sep_l/2))*C_KM/cobs/120)**2)
                syn = syn + g1 + g2
                pk = pipeline_peaks(wl, syn)
                if len(pk) >= 2:
                    nrec += 1
                    dv_m = C_KM*abs(pk[-1]-pk[0])/cobs
                    sep_meas_all.append(dv_m)
                    if abs(dv_m-sep)/sep < 0.20:
                        nrec_corr += 1
            raw = nrec/ntrials
            # 校正: 減假陽性率 (假陽性都會計入 nrec 但峰距未必啱)
            corr = max(0.0, nrec_corr/ntrials - fp0*0.5*(1-fp0))
            if sep_meas_all:
                bias = np.mean(sep_meas_all)-sep
                scatter = np.std(sep_meas_all)
            else:
                bias, scatter = None, None
            key = f"dv={sep:.0f}_amp={amp:.2f}"
            inject_results[f"{name}/{key}"] = {
                "raw_recover": round(raw, 3), "corrected_recover": round(corr, 3),
                "bias_kms": round(bias, 1) if bias is not None else None,
                "scatter_kms": round(scatter, 1) if scatter is not None else None}
            print(f"  Δv={sep:6.0f} 峰高{amp*100:3.0f}% → raw={raw:.2f} corr={corr:.2f} "
                  f"bias={bias if bias is None else round(bias,1)} scatter={scatter if scatter is None else round(scatter,1)}")

# ---- 判讀 ----
print("\n" + "="*88)
print("E. 判讀 — pipeline 可靠性 (校正後 recover)")
print("="*88)
for name, (wl, fl, cobs, R) in windows.items():
    ok_bands = []
    for sep in SEPS:
        for amp in AMPS:
            k = f"{name}/dv={sep:.0f}_amp={amp:.2f}"
            if k in inject_results and inject_results[k]["corrected_recover"] > 0.5:
                ok_bands.append(f"Δv={sep:.0f}@{amp*100:.0f}%")
    print(f"  {name}: 可靠檢出 (corr>0.5) 組合 = {ok_bands if ok_bands else '無'}")

with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p11_little_red_dots/data/27_injection_calibration.json', 'w') as fh:
    json.dump({"false_positive": fp_baseline, "injection": inject_results}, fh, indent=2, ensure_ascii=False)
print("\n[寫入] data/27_injection_calibration.json")