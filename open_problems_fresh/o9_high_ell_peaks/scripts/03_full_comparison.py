#!/usr/bin/env python3
"""
O9: 高 ℓ 峰 — 完整三數據對比 (核心 script)
============================================
數據源:
1. Planck 2018 binned TT (ACT DR4 repo 提供, C_ℓ μK², ℓ=32..2492)
2. SPT-3G D1 TT 150x150 bandpowers (Camphuis et al. 2025, D_ℓ μK²)
3. CAMB raw unlensed (Planck 2018 fiducial, 本機)
vs IDCM 公式: ℓ_m = 44×(M−C(9−m,2)) + ((m−1)×9 mod 25)
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def idcm_peak(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

print("="*78)
print("O9: 高 ℓ 峰 — IDCM vs Planck binned vs SPT-3G D1 vs CAMB")
print("="*78)
print(f"IDCM: { {m: idcm_peak(m) for m in range(1,9)} }")

# ---------- 1. Planck binned ----------
print("\n" + "-"*78)
print("1. Planck 2018 binned TT (C_ℓ μK² → D_ℓ)")
print("-"*78)
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]; err_p = planck[:,2]
from scipy.interpolate import interp1d
C_int = interp1d(ell_p, C_p, kind='cubic', fill_value='extrapolate')
ell_i = np.arange(30, 2500)
D_p = C_int(ell_i) * ell_i*(ell_i+1)/(2*np.pi)
# 峰偵測 (多 sigma)
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
for sigma in [2, 3, 5]:
    s = gaussian_filter1d(D_p, sigma=sigma)
    pk = [int(ell_i[p]) for p in find_peaks(s, distance=30)[0] if 300 < ell_i[p] < 2000]
    print(f"  sigma={sigma}: {pk}")

# ---------- 2. SPT-3G D1 TT 150x150 ----------
print("\n" + "-"*78)
print("2. SPT-3G D1 TT 150x150 (bandpowers, D_ℓ μK²)")
print("-"*78)
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
print(f"  bdp 總值數: {len(bdp)}")
# 每 spectrum 嘅 bin 數 (按 spectra_info 順序)
spec_list = [
    ('TT 90x90',52), ('TE 90x90',72), ('EE 90x90',72), ('TT 90x150',52),
    ('TE 90x150',72), ('TE 150x90',72), ('EE 90x150',72), ('TT 90x220',52),
    ('TE 90x220',72), ('TE 220x90',72), ('EE 90x220',72), ('TT 150x150',52),
    ('TE 150x150',72), ('EE 150x150',72), ('TT 150x220',52), ('TE 150x220',72),
    ('TE 220x150',72), ('EE 150x220',72), ('TT 220x220',52), ('TE 220x220',72),
    ('EE 220x220',72),
]
idx = 0
pos = {}
for name, n in spec_list:
    pos[name] = (idx, idx+n)
    idx += n
print(f"  總計預期: {idx} (檔案有 {len(bdp)})")

# TT 150x150 = 第 12 個 (index 660-712)
lo, hi = pos['TT 150x150']
tt150 = bdp[lo:hi]
print(f"  TT 150x150 bins: {len(tt150)}, 範圍 D_ℓ = {tt150[0]:.0f}..{tt150[-1]:.0f}")

# bin center 由 window function 攞 (每 column argmax)
win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
print(f"  window 形狀: {win.shape}")
ell_w = win[:, 0]
n_bins = win.shape[1] - 1
print(f"  bins: {n_bins}")
bin_centers = []
for b in range(1, n_bins+1):
    peak_idx = np.argmax(win[:, b])
    bin_centers.append(ell_w[peak_idx])
bin_centers = np.array(bin_centers)
print(f"  bin centers (前12): {bin_centers[:12].astype(int)}")
print(f"  bin centers (後12): {bin_centers[-12:].astype(int)}")

# 峰偵測 on TT 150x150 (D_ℓ 直接用)
print("\n  SPT-3G D1 TT 150x150 峰偵測:")
s_spt = gaussian_filter1d(tt150, sigma=1)
pk_spt = [int(bin_centers[p]) for p in find_peaks(s_spt, distance=2)[0]]
print(f"  sigma=1: {pk_spt}")
s_spt3 = gaussian_filter1d(tt150, sigma=3)
pk_spt3 = [int(bin_centers[p]) for p in find_peaks(s_spt3, distance=2)[0]]
print(f"  sigma=3: {pk_spt3}")

# ---------- 3. CAMB ----------
print("\n" + "-"*78)
print("3. CAMB raw unlensed")
print("-"*78)
import camb
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, tau=0.0544)
pars.InitPower.set_params(ns=0.9649, As=2.1e-9)
pars.set_for_lmax(3000, lens_potential_accuracy=0)
TTc = camb.get_results(pars).get_cmb_power_spectra(raw_cl=True)['unlensed_scalar'][:,0]
ell_c = np.arange(len(TTc))
Dl_c = TTc * ell_c*(ell_c+1)/(2*np.pi)
s_c = gaussian_filter1d(Dl_c, sigma=3)
pk_camb = [int(l) for l in find_peaks(s_c, distance=30)[0] if 300 < l < 2000]
print(f"  CAMB raw 峰: {pk_camb}")

# ---------- 4. 主對比表 ----------
print("\n" + "="*78)
print("4. 主對比: IDCM vs 觀測 vs CAMB")
print("="*78)
# 用 Planck binned sigma=3 峰做觀測基準 (涵蓋低ℓ)
s3p = gaussian_filter1d(D_p, sigma=3)
pk_planck_s3 = [int(ell_i[p]) for p in find_peaks(s3p, distance=30)[0] if 100 < ell_i[p] < 2000]
print(f"\nPlanck binned (σ=3) 峰: {pk_planck_s3}")
print(f"SPT-3G D1 峰 (σ=3):      {pk_spt3}")
print(f"CAMB raw (σ=3) 峰:       {pk_camb}")

def match_table(pred_list, obs_peaks, label):
    print(f"\n  {label}:")
    for m, pred in pred_list.items():
        diffs = np.abs(np.array(obs_peaks) - pred)
        j = np.argmin(diffs)
        dev = diffs[j]/pred*100
        mark = "✅" if dev < 2 else ("🟡" if dev < 5 else "❌")
        print(f"    m={m}: IDCM {pred:5d} vs {label} {obs_peaks[j]:5d} → {dev:5.2f}% {mark}")

match_table({m: idcm_peak(m) for m in range(1,8)}, pk_planck_s3, "Planck")
match_table({m: idcm_peak(m) for m in range(4,8)}, pk_spt3, "SPT-3G")
match_table({m: idcm_peak(m) for m in range(1,8)}, pk_camb, "CAMB")

# ---------- 5. 高ℓ區詳細: SPT-3G D1 喺 IDCM m=5,6,7 附近有冇峰? ----------
print("\n" + "-"*78)
print("5. SPT-3G D1 高ℓ區詳細 (1100-1500)")
print("-"*78)
mask = (bin_centers > 1000) & (bin_centers < 1600)
for l, d in zip(bin_centers[mask], tt150[mask]):
    print(f"    ℓ={l:6.1f}  D_ℓ={d:9.1f}")

# ---------- 6. 結論 ----------
print("\n" + "="*78)
print("6. 初步結論")
print("="*78)
