#!/usr/bin/env python3
"""
O9: 高 ℓ 峰 vs 真實觀測數據 (Planck binned + SPT-3G D1)
========================================================
核心問題: IDCM m=4,5,6,7 (1014/1199/1340/1412) vs CAMB raw (1129/1427)
究竟真實觀測峰位支持邊邊個?

數據:
1. Planck 2018 binned TT (ACT DR4 repo 提供, C_ℓ 單位, ℓ=32..2492)
2. SPT-3G D1 TT bandpowers (spt_candl_data, 高ℓ 專精)
3. CAMB raw unlensed (本機生成)

方法:
- Planck binned 譜: 轉 D_ℓ, 平滑, find_peaks → 峰位
- SPT-3G D1: 讀 subset yaml 攞 TT bandpower 範圍 → 轉 D_ℓ → 峰偵測
- IDCM 公式: ℓ_m = 44×(M−C(9−m,2)) + ((m−1)×9 mod 25)
- 逐峰配對 + 偏差表
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# ---------- IDCM 公式 ----------
M, Nd = 33, 44
def idcm_peak(m):
    N_int = M - _m.comb(9-m, 2)
    frac = ((m-1)*9) % 25
    return 44*N_int + frac

idcm_preds = {m: idcm_peak(m) for m in range(1, 9)}
print("="*75)
print("O9: 高 ℓ 峰 — IDCM vs 觀測 vs CAMB")
print("="*75)
print(f"IDCM 預測: { {m: v for m, v in idcm_preds.items()} }")

# ---------- 1. Planck binned TT ----------
print("\n" + "-"*75)
print("1. Planck 2018 binned TT 譜 (ACT DR4 repo 提供)")
print("-"*75)
planck_data = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck_data[:, 0].astype(int)
C_p = planck_data[:, 1]
# D_ℓ = ℓ(ℓ+1)C_ℓ/2π (C_ℓ 單位要乘 1e12 轉 μK²? Planck C_ℓ 檔案通常係 μK² 或 K²)
# ACT 嘅 planck_tt.txt: 睇數值 ~6.5 喺 ℓ=32 — 呢個應該係 D_ℓ (μK²) 或 C_ℓ*1e12
# Planck 2018 TT 譜 D_ℓ(32) ≈ 700 μK² 左右。6.5 太少 — 可能係 C_ℓ×ℓ(ℓ+1)/2π 但以某單位
# 試: 如果 C 喺 μK²: D_ℓ(32) = 32*33/2π * C。C=6.527e-3? 
print(f"  樣本: ℓ={ell_p[0]}, val={planck_data[0,1]:.4e}")
print(f"  範圍: ℓ={ell_p.min()}..{ell_p.max()}, n={len(ell_p)}")
# 檢查單位: 如果值係 D_ℓ (μK²), ℓ=220 應該 ~5700
l220_idx = np.argmin(np.abs(ell_p - 220))
print(f"  ℓ≈220 值 = {planck_data[l220_idx, 1]:.2f}  (Planck D220≈5750 μK²)")

# 峰偵測: 用 D_ℓ 定 C_ℓ 都一樣 (單調轉換)
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

# 內插到整數 ℓ
from scipy.interpolate import interp1d
C_interp = interp1d(ell_p, C_p, kind='cubic', fill_value='extrapolate')
ell_int = np.arange(30, 2500)
C_int = C_interp(ell_int)
D_int = C_int * ell_int * (ell_int+1) / (2*np.pi)

for sigma in [1, 2, 3, 5, 8]:
    s = gaussian_filter1d(D_int, sigma=sigma)
    peaks, props = find_peaks(s, distance=30, prominence=0)
    pk = [int(ell_int[p]) for p in peaks if 100 < ell_int[p] < 2000]
    print(f"  sigma={sigma}: 峰位 = {pk}")

# 用 sigma=3 做標準
s3 = gaussian_filter1d(D_int, sigma=3)
peaks3, _ = find_peaks(s3, distance=30, prominence=0)
pk_planck = [int(ell_int[p]) for p in peaks3 if 100 < ell_int[p] < 2000]
print(f"  → Planck binned 峰 (sigma=3): {pk_planck}")

# ---------- 2. CAMB raw ----------
print("\n" + "-"*75)
print("2. CAMB raw unlensed (Planck 2018 fiducial)")
print("-"*75)
import camb
H0 = 67.36
pars = camb.CAMBparams()
pars.set_cosmology(H0=H0, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000, lens_potential_accuracy=0)
results = camb.get_results(pars)
TT = results.get_cmb_power_spectra(raw_cl=True)['unlensed_scalar'][:, 0]
ell_c = np.arange(len(TT))
Dl_c = TT * ell_c * (ell_c+1) / (2*np.pi)
s_c = gaussian_filter1d(Dl_c, sigma=3)
pk_camb = [int(l) for l in find_peaks(s_c, distance=30, prominence=0)[0] if 100 < l < 2000]
print(f"  CAMB raw 峰: {pk_camb}")

# ---------- 3. SPT-3G D1 TT bandpowers ----------
print("\n" + "-"*75)
print("3. SPT-3G D1 TT bandpowers (Camphuis et al. 2025)")
print("-"*75)
# 讀 subset yaml 攞 TT 佈局
import yaml, re
try:
    with open(os.path.join(DATADIR, 'spt_tne.yaml')) as f:
        cfg = yaml.safe_load(f)
    # spectra_info: TT 150x150 有 52 bins
    print(f"  spectra_info: {cfg['spectra_info']}")
except Exception as e:
    print(f"  yaml 讀取失敗: {e}")

# bdp.txt 係長格式: 每個 spectrum 接住落
# 需要讀 windows 或 index 先知道 TT 150x150 係邊 52 個
# 用 subsets/SPT3G_D1_TT.yaml 攞 bin 數量同排列
import subprocess
r = subprocess.run(['curl', '-sL', '--max-time', '45', '-A', 'Mozilla/5.0',
    'https://raw.githubusercontent.com/SouthPoleTelescope/spt_candl_data/main/spt_candl_data/SPT3G_D1_TnE_v0/subsets/SPT3G_D1_TT.yaml'],
    capture_output=True, text=True)
if r.returncode == 0 and r.stdout:
    with open(os.path.join(DATADIR, 'spt_tt_subset.yaml'), 'w') as f:
        f.write(r.stdout)
    print(f"  TT subset yaml 下載成功 ({len(r.stdout)} bytes)")
    print(r.stdout[:800])
else:
    print("  TT subset yaml 下載失敗")
