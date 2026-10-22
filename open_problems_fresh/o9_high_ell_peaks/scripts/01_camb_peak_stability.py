#!/usr/bin/env python3
"""
O9: CAMB 高 ℓ 峰檢測穩定性分析
================================
問題: IDCM m=5,6,7 (1199/1340/1412) vs CAMB raw (1129/1427) 偏差 5.8-11.3%
CAMB raw m=4 偵測到 1129 但 Planck 官方標定 ℓ₄=1014±5 — CAMB 高ℓ峰偵測可能唔對應 m=4

測試:
1. 唔同平滑 sigma (1,2,3,5,8,10,15) 下 CAMB raw 峰位變化
2. 二階導數零點 (inflection) 偵測 — 峰嘅更穩定代理
3. D_ℓ 幅值 — 阻尼尾峰有幾弱?
4. CAMB raw vs lensed 峰位差異
5. 高分辨率 ℓ 網格 (lmax=6000) 下峰位
"""
import numpy as np
import camb
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# Planck 2018 fiducial
H0 = 67.36
pars = camb.CAMBparams()
pars.set_cosmology(H0=H0, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)

def get_spectra(lmax=3000):
    pars.set_for_lmax(lmax, lens_potential_accuracy=0)
    results = camb.get_results(pars)
    raw = results.get_cmb_power_spectra(raw_cl=True)['unlensed_scalar'][:, 0]
    lensed = results.get_cmb_power_spectra()['total'][:, 0]
    ell = np.arange(len(raw))
    Dl_raw = raw * ell * (ell+1) / (2*np.pi)
    Dl_lens = lensed * ell * (ell+1) / (2*np.pi)
    return ell, Dl_raw, Dl_lens

ell, Dl_raw, Dl_lens = get_spectra(3000)

print("="*70)
print("O9: CAMB 高 ℓ 峰檢測穩定性 (Planck 2018 fiducial)")
print("="*70)

# IDCM 公式
import math as _m
M, Nd = 33, 44
def idcm_peak(m):
    N_int = M - _m.comb(9-m, 2)
    frac = ((m-1)*9) % 25
    return 44*N_int + frac

idcm_preds = {m: idcm_peak(m) for m in range(1, 9)}
print("\nIDCM 預測:", {m: v for m, v in idcm_preds.items()})

# ---------- 1. sigma 掃描 ----------
print("\n" + "-"*70)
print("1. 平滑 sigma 掃描 (raw unlensed, 峰偵測 300-2000)")
print("-"*70)
for sigma in [1, 2, 3, 5, 8, 10, 15]:
    s = gaussian_filter1d(Dl_raw, sigma=sigma)
    peaks, props = find_peaks(s, distance=30, prominence=0)
    # 只保留 >300
    pk = [p for p in peaks if 300 < p < 2000]
    print(f"  sigma={sigma:2d}: {pk}")

# ---------- 2. 幅值: 峰有幾弱? ----------
print("\n" + "-"*70)
print("2. D_ℓ 峰幅值 (raw, 阻尼尾有多弱)")
print("-"*70)
s3 = gaussian_filter1d(Dl_raw, sigma=3)
peaks3, props3 = find_peaks(s3, distance=30, prominence=0)
pk3 = [p for p in peaks3 if 100 < p < 2500]
for p in pk3:
    D = Dl_raw[p]
    ratio = D / Dl_raw[220] * 100
    print(f"  ℓ={p:5d}  D_ℓ={D:10.1f}  = {ratio:6.2f}% of D₁")

# ---------- 3. 二階導數零點 (峰嘅更穩定代理) ----------
print("\n" + "-"*70)
print("3. 二階導數零點 (d²D/dℓ²=0, 峰/谷邊界) — 對平滑更魯棒")
print("-"*70)
d2 = np.gradient(np.gradient(Dl_raw))
# 平滑二階導數
d2s = gaussian_filter1d(d2, sigma=5)
# 零點 = 符號改變
zeros = []
for l in range(400, 2000):
    if d2s[l-1] > 0 > d2s[l]:
        zeros.append(l)  # d² 由正轉負 = 局部極大 (峰)
print(f"  二階導數峰位: {zeros}")

# ---------- 4. raw vs lensed ----------
print("\n" + "-"*70)
print("4. raw vs lensed 峰位 (ℓ 200-2000)")
print("-"*70)
for name, Dl in [("raw   ", Dl_raw), ("lensed", Dl_lens)]:
    s = gaussian_filter1d(Dl, sigma=3)
    peaks, _ = find_peaks(s, distance=30, prominence=0)
    pk = [p for p in peaks if 200 < p < 2000]
    print(f"  {name}: {pk}")

# ---------- 5. IDCM vs CAMB 逐峰配對 ----------
print("\n" + "-"*70)
print("5. IDCM vs CAMB raw (sigma=3) 峰配對 — 逐個 IDCM 峰搵最近 CAMB 峰")
print("-"*70)
for m in range(1, 8):
    pred = idcm_peak(m)
    diffs = np.abs(np.array(pk3) - pred)
    idx = np.argmin(diffs)
    closest = pk3[idx]
    dev = abs(closest - pred)/pred*100
    print(f"  m={m}: IDCM {pred:5d} vs CAMB {closest:5d} → {dev:6.2f}%")

# ---------- 6. 局部峰檢測喺 1014 附近 (m=4 應該喺度) ----------
print("\n" + "-"*70)
print("6. 局部檢查: m=4 (1014), m=5 (1199), m=6 (1340), m=7 (1412) 附近嘅實際譜")
print("-"*70)
for pred_l in [1014, 1199, 1340, 1412]:
    lo, hi = pred_l - 60, pred_l + 60
    # 局部平滑後嘅最大值
    local_max_l = lo + np.argmax(s3[lo:hi])
    D_val = Dl_raw[local_max_l]
    print(f"  IDCM ℓ={pred_l}: 局部 sigma=3 最大喺 ℓ={local_max_l} (D={D_val:.0f})")

# ---------- 7. 高分辨率網格 lmax=6000 ----------
print("\n" + "-"*70)
print("7. 高分辨率 lmax=6000 峰位 (確認 3000 夠唔夠)")
print("-"*70)
ell6, Dl6_raw, _ = get_spectra(6000)
s6 = gaussian_filter1d(Dl6_raw, sigma=3)
pk6 = [p for p in find_peaks(s6, distance=30, prominence=0)[0] if 200 < p < 2000]
print(f"  lmax=6000 峰: {pk6}")
print(f"  與 lmax=3000 一致: {pk6 == pk3}")
