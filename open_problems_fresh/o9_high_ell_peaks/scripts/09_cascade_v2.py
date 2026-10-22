#!/usr/bin/env python3
"""
O9: 修正版振幅級聯 + m=5 結構搜尋
=====================================
用 bin 中心真峰 (唔內插) 做:
1. 峰位 + 振幅 (221/527/815/1013/1121/1337/1400)
2. 相鄰比率 + 有理數擬合 (Rational Fraction Cascade)
3. m=5 結構修正搜尋: 1121/1124 閉合 <1%
   線索: 1199−1124 = 75 = 3×25 = 3×F₅²
   1121 = 44×25+21 (21=F₈)?? 1124 = ?
4. mod-25 相位重排: 有冇可能 m=5 相位唔係 11?
"""
import numpy as np
import math as _m
import os
from fractions import Fraction
from itertools import product

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2

# ---------- 0. 數據 ----------
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]; err_p = planck[:,2]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

# ---------- 1. 真峰序列 (bin 中心局部極大) ----------
print("="*80)
print("O9: 修正版 — 真峰振幅級聯")
print("="*80)

# IDCM 預測
def idcm_peak(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)
idcm_preds = {m: idcm_peak(m) for m in range(1, 8)}
print(f"\nIDCM 預測: {idcm_preds}")

# 喺每個 IDCM 預測 ±15 內搵 bin 中心局部極大 (最高嗰個)
print("\n峰位配對 (IDCM ±15 內嘅 bin 局部極大):")
peak_data = {}
for m, pred in idcm_preds.items():
    win = 60 if m == 5 else 15  # m=5 用大窗
    mask = np.abs(ell_p - pred) <= win
    idxs = np.where(mask)[0]
    # 喺窗內搵局部極大
    local_max = []
    for i in idxs:
        if i > 0 and i < len(ell_p)-1:
            if D_bin[i] >= D_bin[i-1] and D_bin[i] >= D_bin[i+1]:
                local_max.append((ell_p[i], D_bin[i]))
            elif i == idxs[0] or i == idxs[-1]:
                local_max.append((ell_p[i], D_bin[i]))
    if local_max:
        l_peak, D_peak = max(local_max, key=lambda x: x[1])
        peak_data[m] = (l_peak, D_peak)
        dev = (l_peak - pred)/pred*100
        mark = "✅" if abs(dev) < 2 else ("🟡" if abs(dev) < 5 else "❌")
        print(f"   m={m}: IDCM {pred} → bin 峰 ℓ={l_peak} (D={D_peak:.1f}) dev={dev:+.2f}% {mark}")

# ---------- 2. 振幅級聯 ----------
print("\n" + "-"*80)
print("2. 相鄰峰值比率 A_{m+1}/A_m (有理數擬合)")
print("-"*80)
ratios = {}
for m in range(1, 7):
    if m in peak_data and m+1 in peak_data:
        r = peak_data[m+1][1] / peak_data[m][1]
        ratios[m] = r
        fr = Fraction(r).limit_denominator(30)
        dev = abs(r - fr.numerator/fr.denominator)/r*100
        print(f"   A_{m+1}/A_{m} = {r:.4f} ≈ {fr.numerator}/{fr.denominator} ({fr.numerator/fr.denominator:.4f}) dev={dev:.2f}%")

print("\n   歸一化 A_m/A_1:")
A1 = peak_data[1][1]
for m in range(1, 8):
    if m in peak_data:
        a = peak_data[m][1] / A1
        fr = Fraction(a).limit_denominator(40)
        dev = abs(a - fr.numerator/fr.denominator)/a*100
        print(f"   A_{m}/A_1 = {a:.4f} ≈ {fr.numerator}/{fr.denominator} ({fr.numerator/fr.denominator:.4f}) dev={dev:.2f}%")

# ---------- 3. ε 結構 ----------
print("\n" + "-"*80)
print("3. ε=φ⁻¹/4 結構 (IDCM 標準):")
print("-"*80)
eps = phi**-1/4
print(f"   ε = {eps:.5f}")
print(f"   3ε = {3*eps:.5f} (A₂/A₁ 原閉合 1.6%)")
print(f"   4/9 = {4/9:.5f} (A₂/A₁ 新擬合 0.23%)")
print(f"   4/9 vs 3ε: 差 {(4/9)/(3*eps)-1:.2%}")
# 4/9 = (2/3)² 平方? 有意思
print(f"   4/9 = (2/3)² — 平方結構!")
print(f"   而 2/3 = φ⁻¹×? φ⁻¹=0.618, 2/3=0.667, 差 7.3%")
print(f"   5/8 = φ⁻¹²? φ⁻²=0.382, φ⁻¹=0.618, 5/8=0.625 ≈ φ⁻¹ (1.1%)!")

# ---------- 4. m=5 結構搜尋 ----------
print("\n" + "-"*80)
print("4. m=5 修正搜尋 (目標: 1121/1124 閉合)")
print("-"*80)
print(f"   觀測真峰: 1121 (Planck bin), 1124 (SPT-3G), 1129 (CAMB)")
print(f"   IDCM 原: 1199 (44×27+11)")
print(f"   偏差: 1199−1121 = 78, 1199−1124 = 75 = 3×25 = 3×F₅²")
print(f"   1121 = 44×25 + 21  (21 = F₈)")
print(f"   1124 = 44×25 + 24  (24 = ?)")
print(f"   1124/44 = 25.545")

# 搜尋: 有冇簡單結構 44×N + f 匹配 1121/1124?
print("\n   44×N + f 分解 (N=20..30, f=0..43):")
for target in [1121, 1124]:
    print(f"   target = {target}:")
    for N in range(20, 31):
        f = target - 44*N
        if 0 <= f < 44:
            # f 係咪有趣數?
            interesting = ""
            if f in [9, 18, 2, 11, 20, 4, 21, 13, 24, 25]:
                interesting = " ← mod-25 序列成員!"
            print(f"     44×{N} + {f} = {44*N+f}{interesting}")

# mod-25 相位序列檢查
print("\n   mod-25 相位序列 ((m−1)×9 mod 25):")
phases = [((m-1)*9) % 25 for m in range(1, 9)]
print(f"   {phases}")
print(f"   如果 m=5 相位改用 24 或 21?")
for f5 in [21, 24, 11]:
    # 保持其他 m 原相位
    seq = phases.copy()
    seq[4] = f5
    peaks = [44*(33 - _m.comb(9-m, 2)) + seq[m-1] for m in range(1, 8)]
    dev5 = (1124 - peaks[4])/1124*100
    print(f"   m=5 相位={f5}: {peaks} → m=5={peaks[4]} vs 1124 dev={dev5:.2f}%")

# ---------- 5. 線性擬合 vs 觀測 ----------
print("\n" + "-"*80)
print("5. 峰位 vs m 結構: 線性/二次擬合")
print("-"*80)
obs_l = np.array([peak_data[m][0] for m in range(1, 8)])
ms = np.arange(1, 8)
# 二次擬合
coef = np.polyfit(ms, obs_l, 2)
print(f"   二次擬合: ℓ(m) = {coef[0]:.2f}m² + {coef[1]:.2f}m + {coef[2]:.2f}")
fit2 = np.polyval(coef, ms)
print(f"   擬合值: {[f'{v:.0f}' for v in fit2]}")
print(f"   殘差: {[f'{v:.1f}' for v in obs_l - fit2]}")

# 3 段線性 (低/中/高ℓ)
print(f"\n   峰間距 (觀測): {np.diff(obs_l)}")
print(f"   峰間距 (IDCM): {[idcm_preds[m+1]-idcm_preds[m] for m in range(1,7)]}")
print(f"   觀測 Δℓ 比率: {[f'{np.diff(obs_l)[i+1]/np.diff(obs_l)[i]:.3f}' for i in range(5)]}")

# 保存
import json
out = {"peaks_bin": {str(m): [int(l), float(D)] for m, (l, D) in peak_data.items()},
       "ratios": {str(m): float(r) for m, r in ratios.items()},
       "A1": float(A1), "eps": float(eps)}
with open(os.path.join(DATADIR, 'peak_data_v2.json'), 'w') as f:
    json.dump(out, f, indent=2)
print("\n   已保存 peak_data_v2.json")
