#!/usr/bin/env python3
"""
O9: 峰位真實性 + 振幅級聯 (Rational Fraction Cascade) 分析
=============================================================
1. Planck binned 真實峰位檢查: bin 結構 + 局部極大 (唔內插)
   — 驗證 1014 係咪真峰 (950 更高?)
2. 峰振幅提取: D_ℓ 峰值 (μK²)
3. 相鄰峰值比率 A_{m+1}/A_m + 有理數擬合 (Fraction)
4. 歸一化振幅序列 A_m/A_1 級聯結構
5. 對比 IDCM ε=φ⁻¹/4 結構
"""
import numpy as np
import math as _m
import os
from fractions import Fraction

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

print("="*80)
print("O9: 峰位真實性 + 振幅級聯 (Rational Fraction Cascade)")
print("="*80)

# ---------- 0. bin 結構檢查 ----------
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]; err_p = planck[:,2]
print(f"\nbin 總數: {len(ell_p)}, ℓ 範圍: {ell_p.min()}..{ell_p.max()}")
dells = np.diff(ell_p)
print(f"bin 寬度分佈: min={dells.min()}, max={dells.max()}")
# 邊度變闊?
wide_idx = np.where(dells > 6)[0]
if len(wide_idx):
    print(f"bin 變闊位置: ℓ={ell_p[wide_idx[0]]}.. (Δℓ={dells[wide_idx[0]]})")
    print(f"   ℓ={ell_p[wide_idx[0]]} 前後: {ell_p[max(0,wide_idx[0]-3):wide_idx[0]+4]}")

# ---------- 1. 850-1150 完整區間 (m=4 真實性檢查) ----------
print("\n" + "-"*80)
print("1. 850-1160 區間詳細 (m=4 峰真實性)")
print("-"*80)
for i, l in enumerate(ell_p):
    if 850 <= l <= 1160:
        D = C_p[i]*l*(l+1)/(2*np.pi)
        print(f"   ℓ={l:5d}  D_ℓ={D:8.1f}  σ_D={err_p[i]*l*(l+1)/(2*np.pi):6.1f}")

# ---------- 2. 全譜峰偵測 (bin 中心, sigma=1 輕平滑) ----------
print("\n" + "-"*80)
print("2. 全譜峰偵測 (bin 中心 + sigma=1)")
print("-"*80)
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)
s1 = gaussian_filter1d(D_bin, sigma=1)
cand, props = find_peaks(s1, distance=3, prominence=5)
cand = np.array(cand); proms = np.array(props['prominences'])
keep = (proms > 0.01*s1[cand]) & (s1[cand] > 100)
peaks = [(ell_p[c], D_bin[c], s1[c]) for c in cand[keep]]
print(f"  偵測峰數: {len(peaks)}")
for l, D, s in peaks:
    print(f"   ℓ={l:5d}  D_raw={D:8.1f}  D_sm={s:8.1f}")

# ---------- 3. 主峰序列 (人擇挑選: 220, ~537, ~810, ~1014, ~1124, ~1340, ~1412) ----------
print("\n" + "-"*80)
print("3. 峰振幅 + 相鄰比率 (主峰序列)")
print("-"*80)
# 用局部視窗搵每個 IDCM 預測附近嘅真實 bin 最大
idcm_preds = {1:220, 2:537, 3:810, 4:1014, 5:1199, 6:1340, 7:1412}
peak_data = {}
for m, pred in idcm_preds.items():
    # 視窗 ±40 (m=5 用 ±100 因為偏差大)
    win = 100 if m == 5 else 40
    mask = np.abs(ell_p - pred) <= win
    if mask.sum() == 0:
        print(f"   m={m}: 視窗內冇 bin!")
        continue
    idx = np.argmax(D_bin[mask])
    l_peak = ell_p[mask][idx]
    D_peak = D_bin[mask][idx]
    peak_data[m] = (l_peak, D_peak)
    print(f"   m={m}: ℓ={l_peak}  D_ℓ={D_peak:8.1f}")

print("\n   相鄰峰值比率 A_{m+1}/A_m:")
ratios = {}
for m in range(1, 7):
    if m in peak_data and m+1 in peak_data:
        r = peak_data[m+1][1] / peak_data[m][1]
        ratios[m] = r
        # 最簡有理數 (分母 ≤ 30)
        fr = Fraction(r).limit_denominator(30)
        print(f"   A_{m+1}/A_{m} = {r:.4f} ≈ {fr.numerator}/{fr.denominator} = {fr.numerator/fr.denominator:.4f} (偏差 {abs(r - fr.numerator/fr.denominator)/r*100:.2f}%)")

print("\n   歸一化振幅 A_m/A_1:")
A1 = peak_data[1][1]
for m in range(1, 8):
    if m in peak_data:
        a = peak_data[m][1] / A1
        fr = Fraction(a).limit_denominator(30)
        print(f"   A_{m}/A_1 = {a:.4f} ≈ {fr.numerator}/{fr.denominator} = {fr.numerator/fr.denominator:.4f} (偏差 {abs(a - fr.numerator/fr.denominator)/a*100:.2f}%)")

# ---------- 4. IDCM ε 結構對比 ----------
print("\n" + "-"*80)
print("4. IDCM ε=φ⁻¹/4 結構對比")
print("-"*80)
phi = (1 + 5**0.5)/2
eps = phi**-1 / 4
print(f"   ε = φ⁻¹/4 = {eps:.6f}")
print(f"   3ε = {3*eps:.6f}")
print(f"   2ε = {2*eps:.6f}")
print(f"   ε/2 = {eps/2:.6f}")
print(f"   ε×φ = {eps*phi:.6f}  (=φ⁻²/4)")
# 檢查比率同 ε 倍數嘅關係
if ratios:
    print("\n   相鄰比率 vs ε 倍數:")
    for m, r in ratios.items():
        best_k = r / eps
        print(f"   A_{m+1}/A_{m} = {r:.4f} = {best_k:.3f} × ε")

# ---------- 5. 誤差棒 ----------
print("\n" + "-"*80)
print("5. 峰振幅誤差 (σ 傳播)")
print("-"*80)
for m, (l, D) in peak_data.items():
    i = np.where(ell_p == l)[0][0]
    sigD = err_p[i]*l*(l+1)/(2*np.pi)
    print(f"   m={m}: D_ℓ({l}) = {D:.1f} ± {sigD:.1f} μK²")

# ---------- 6. 保存結果 ----------
print("\n" + "-"*80)
print("6. 保存 peak_data.json")
print("-"*80)
import json
out = {"peaks": {str(m): {"ell": int(l), "D": float(D)} for m, (l, D) in peak_data.items()},
       "ratios": {str(m): float(r) for m, r in ratios.items()},
       "A1": float(A1), "eps": float(eps)}
with open(os.path.join(DATADIR, 'peak_data.json'), 'w') as f:
    json.dump(out, f, indent=2)
print("   已保存:", os.path.join(DATADIR, 'peak_data.json'))
