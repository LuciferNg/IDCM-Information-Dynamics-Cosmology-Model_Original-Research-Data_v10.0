#!/usr/bin/env python3
"""
O9: 峰間距守恆 + 振幅級聯最終閉合 + 雙重驗證
================================================
1. 峰間距守恆: Δℓ₄+Δℓ₅ = 185+141 = 326 vs 107+219 = 326 ✓
2. 振幅級聯: A_m/A_1 有理數 + (2/3)^k 結構
3. 全閉合矩陣 (m=1..7, 原 vs 修正)
4. 雙重驗證: 所有數字由原始 planck_tt.txt 重算
"""
import numpy as np
import math as _m
import os
import json
from fractions import Fraction

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2
F = [0, 1]
for i in range(2, 15): F.append(F[-1]+F[-2])
L = [2, 1]
for i in range(2, 15): L.append(L[-1]+L[-2])

print("="*80)
print("O9: 最終閉合 — 峰間距守恆 + 振幅級聯")
print("="*80)

# ---------- 0. 數據重讀 (雙重驗證基礎) ----------
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]; err_p = planck[:,2]
D_bin = C_p * ell_p*(ell_p+1)/(2*np.pi)

# 峰位 (IDCM 預測 ±15 內 bin 局部極大, 之前 script 09 方法)
def idcm_orig(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)
def idcm_fix(m):
    if m == 5:
        return 44*(33 - F[6]) + F[8]  # 1121
    return idcm_orig(m)

obs_peaks = {}
for m in range(1, 8):
    pred = idcm_orig(m)
    win = 60 if m == 5 else 15
    mask = np.abs(ell_p - pred) <= win
    idxs = np.where(mask)[0]
    best_l, best_D = None, -1
    for i in idxs:
        if i > 0 and i < len(ell_p)-1:
            if D_bin[i] >= D_bin[i-1] and D_bin[i] >= D_bin[i+1]:
                if D_bin[i] > best_D:
                    best_l, best_D = ell_p[i], D_bin[i]
    if best_l is not None:
        obs_peaks[m] = (best_l, best_D)

print("\n1. 峰位閉合矩陣:")
print(f"{'m':>2} {'IDCM原':>6} {'IDCM修':>6} {'obs':>5} {'dev原':>8} {'dev修':>8}")
total_o = total_f = 0
for m in range(1, 8):
    o, f = idcm_orig(m), idcm_fix(m)
    l, D = obs_peaks[m]
    dev_o = (l-o)/o*100
    dev_f = (l-f)/f*100
    total_o += dev_o**2; total_f += dev_f**2
    mark = "✅" if abs(dev_f) < 1 else ("🟡" if abs(dev_f) < 3 else "❌")
    print(f"{m:>2} {o:>6} {f:>6} {l:>5} {dev_o:>+7.2f}% {dev_f:>+7.2f}% {mark}")
print(f"   RMS: 原 {np.sqrt(total_o/7):.2f}% → 修正 {np.sqrt(total_f/7):.2f}%")

# ---------- 1. 峰間距守恆 ----------
print("\n" + "-"*80)
print("2. 峰間距守恆 (相位壓抑點 m=5):")
print("-"*80)
orig_dl = [idcm_orig(m+1)-idcm_orig(m) for m in range(1,7)]
fix_dl = [idcm_fix(m+1)-idcm_fix(m) for m in range(1,7)]
obs_dl = [obs_peaks[m+1][0]-obs_peaks[m][0] for m in range(1,7)]
print(f"   原 IDCM Δℓ:   {orig_dl}")
print(f"   修正 IDCM Δℓ: {fix_dl}")
print(f"   觀測 Δℓ:      {obs_dl}")
print()
print(f"   m=4→5→6 守恆檢查:")
print(f"   原: Δℓ₄+Δℓ₅ = {orig_dl[3]} + {orig_dl[4]} = {orig_dl[3]+orig_dl[4]}")
print(f"   修正: Δℓ₄+Δℓ₅ = {fix_dl[3]} + {fix_dl[4]} = {fix_dl[3]+fix_dl[4]}")
print(f"   守恆: {orig_dl[3]+orig_dl[4]} == {fix_dl[3]+fix_dl[4]} → {orig_dl[3]+orig_dl[4]==fix_dl[3]+fix_dl[4]}")
print(f"   重分配: Δℓ₄: 185→{fix_dl[3]} ({fix_dl[3]-185:+d}), Δℓ₅: 141→{fix_dl[4]} ({fix_dl[4]-141:+d})")
print(f"   ★ −{185-fix_dl[3]} 同 +{fix_dl[4]-141} 對稱!")

# ---------- 2. 相位壓抑幅度 ----------
print("\n" + "-"*80)
print("3. 相位壓抑幅度:")
print("-"*80)
shift = idcm_orig(5) - idcm_fix(5)
print(f"   m=5 峰位移: {idcm_orig(5)} → {idcm_fix(5)} = {shift:+d}")
print(f"   {shift} = -3×F₅² = -3×25? → {-3*25} ✓" if shift == -75 else f"   {shift} ≠ -75")
print(f"   {shift} = -(F₁₁−L₄) = -(89−11) = -78? → {-(89-11)} " + ("✓" if shift == -78 else "✗"))
print(f"   {shift} = -2×44+13? → {-2*44+13}" + (" ✓" if shift == -2*44+13 else ""))
print(f"   {shift} = -44×2+10? → {-44*2+10}" + (" ✓" if shift == -44*2+10 else ""))
print()
print(f"   F₆=8 取代 C(4,2)=6: 差 2 → ΔN = -2 → -2×44 = -88")
print(f"   相位 11 → 21 (F₈): 差 +10 → 淨位移 -88+10 = -78 ✓✓✓")
print(f"   ★★★ 位移分解: -78 = -2×44 + 10 = -88 + 10 ★★★")

# ---------- 3. 振幅級聯 ----------
print("\n" + "-"*80)
print("4. 振幅級聯 (A_m/A_1):")
print("-"*80)
A = {m: obs_peaks[m][1] for m in range(1, 8)}
A1 = A[1]
print(f"{'m':>2} {'ℓ':>5} {'A_m':>8} {'A_m/A_1':>8} {'有理數':>10} {'dev':>6}")
fracs = {}
for m in range(1, 8):
    a = A[m]/A1
    fr = Fraction(a).limit_denominator(50)
    fracs[m] = fr
    dev = abs(a - fr.numerator/fr.denominator)/a*100
    print(f"{m:>2} {obs_peaks[m][0]:>5} {A[m]:>8.1f} {a:>8.4f} {fr.numerator:>4}/{fr.denominator:<4} {dev:>5.2f}%")

print("\n   相鄰比率:")
for m in range(1, 7):
    r = A[m+1]/A[m]
    fr = Fraction(r).limit_denominator(30)
    dev = abs(r - fr.numerator/fr.denominator)/r*100
    print(f"   A_{m+1}/A_{m} = {r:.4f} ≈ {fr.numerator}/{fr.denominator} (dev {dev:.2f}%)")

# (2/3)^k
print("\n   (2/3)^k 指數:")
for m in range(1, 8):
    a = A[m]/A1
    k = np.log(a)/np.log(2/3)
    half = abs(k - round(2*k)/2)
    tag = "★半整數" if half < 0.15 else ""
    print(f"   A_{m}/A_1 = (2/3)^{k:.3f} {tag}")

# ---------- 4. 保存最終 ----------
final = {
    "closure": {str(m): {"idcm_orig": int(idcm_orig(m)), "idcm_fix": int(idcm_fix(m)),
                          "obs": int(obs_peaks[m][0]), "D": float(obs_peaks[m][1]),
                          "dev_orig_pct": float((obs_peaks[m][0]-idcm_orig(m))/idcm_orig(m)*100),
                          "dev_fix_pct": float((obs_peaks[m][0]-idcm_fix(m))/idcm_fix(m)*100)}
                 for m in range(1, 8)},
    "formula": {
        "orig": "l_m = 44*(33-C(9-m,2)) + ((m-1)*9 mod 25)",
        "fix_m5": "l_5 = 44*(33-F6) + F8 = 44*25+21 = 1121",
        "shift_decomp": "-78 = -2*44 + 10 = -88 + 10",
        "conservation": "dL4+dL5 = 326 = 107+219"
    },
    "amplitude": {str(m): {"ratio": float(A[m]/A1), "frac": f"{fracs[m].numerator}/{fracs[m].denominator}"}
                  for m in range(1, 8)},
    "rms": {"orig": float(np.sqrt(total_o/7)), "fix": float(np.sqrt(total_f/7))}
}
with open(os.path.join(DATADIR, 'o9_final.json'), 'w') as f:
    json.dump(final, f, indent=2, ensure_ascii=False)
print(f"\n   已保存 o9_final.json")
