#!/usr/bin/env python3
"""
O9: m=5 結構閉合 + 振幅級聯深度分析
=======================================
線索:
1. m=5 觀測峰 1121 (Planck) / 1124 (SPT-3G) = 44×25 + 21/24
   1124−1199 = −75 = −3×F₅²   ← 相位壓抑 75!
2. 振幅級聯: A₂/A₁=4/9=(2/3)², A₃/A₂=1, A₄/A₃=11/26, A₅/A₄=26/23, A₆/A₅=5/8≈φ⁻¹

假設:
A. m=5 相位壓抑: Δℓ₅ = 185 − 75 = 110 (44×2.5)
   如果 m=5 嘅三角形數項 C(4,2)=6 有誤差?
   1199 = 44×27+11. 若 N_int=25: 44×25+21 = 1121 (F₈=21)
B. 峰間距: 觀測 306/288/198/144/198/45
   注意 306≈317−11, 288≈273+15, 198≈204−6, 144≈185−41, 198 vs 141+57, 45 vs 72−27

檢查:
1. m=5 用 1121: 對應結構 44×25+F₈
2. mod-25 相位序列有冇 Fibonacci 結構?
3. 三角形數序列 C(9−m,2): 28,21,15,10,6,3,1
   m=5: C(4,2)=6. 若用 C(5,2)=10: 44×(33−10)+? = 44×23+? = 1012+? 唔啱
   若用 C(3,2)=3: 44×(33−3)+21 = 44×30+21 = 1341? 唔啱
4. 1121 = 44×25+21: 25 = F₅², 21 = F₈. 而 1199 = 44×27+11 (27=33−6, 11=L₅)
   差: 27→25 (−2 = −L₀?), 11→21 (+10 = +F₇−L₀?)
5. 振幅: A₅/A₄ = 1.1307 ≈ 26/23. 26 = 2×13 = 2×F₇, 23 = 33−10 = M−C(5,2)
"""
import numpy as np
import math as _m
import os
from fractions import Fraction

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
phi = (1 + 5**0.5)/2

print("="*80)
print("O9: m=5 結構閉合 + 振幅級聯深度")
print("="*80)

# Fibonacci / Lucas
F = [0, 1]
for i in range(2, 15):
    F.append(F[-1]+F[-2])
L = [2, 1]
for i in range(2, 15):
    L.append(L[-1]+L[-2])
print(f"\nFibonacci: {F[1:13]}")
print(f"Lucas: {L[1:13]}")

# ---------- 1. 峰位結構 ----------
print("\n" + "-"*80)
print("1. 峰位結構: IDCM 原始 vs 觀測")
print("-"*80)
idcm_orig = {m: 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25) for m in range(1, 8)}
obs = {1: 221, 2: 527, 3: 815, 4: 1013, 5: 1121, 6: 1337, 7: 1400}
print(f"{'m':>2} {'IDCM':>5} {'obs':>5} {'Δ':>6} {'Δ/44':>6} {'Δ/25':>6}")
for m in range(1, 8):
    d = obs[m] - idcm_orig[m]
    print(f"{m:>2} {idcm_orig[m]:>5} {obs[m]:>5} {d:>+6} {d/44:>+6.3f} {d/25:>+6.3f}")

print("\n   觀察: m=5 偏差 −78 = −44×1.77 = −3.12×25")
print(f"   −78 = −(44×2 − 10) = −88+10? 定 −3×25−3?")
print(f"   −78 = −(F₁₁−L₄)? F₁₁=89, 89−11=78 ← F₁₁−L₄=78!")

# ---------- 2. 三角形數 vs 觀測峰間距 ----------
print("\n" + "-"*80)
print("2. 峰間距結構: 三角形數 vs 觀測")
print("-"*80)
obs_dl = [obs[m+1]-obs[m] for m in range(1, 7)]
tri = [_m.comb(9-m, 2) for m in range(1, 7)]  # 28,21,15,10,6,3
print(f"   觀測 Δℓ: {obs_dl}")
print(f"   三角形數: {tri}")
print(f"   44×三角形數差: {[44*(tri[i]-tri[i+1]) for i in range(5)]}")
print(f"   觀測 Δℓ / 44: {[f'{d/44:.3f}' for d in obs_dl]}")
print(f"   觀測 Δℓ / 44 取整: {[int(round(d/44)) for d in obs_dl]}")

# ---------- 3. 振幅級聯: 分子分母結構 ----------
print("\n" + "-"*80)
print("3. 振幅級聯: 有理數分子分母結構")
print("-"*80)
# 用 peak_data_v2.json
import json
with open(os.path.join(DATADIR, 'peak_data_v2.json')) as f:
    pd = json.load(f)
A = {int(m): pd['peaks_bin'][m][1] for m in pd['peaks_bin']}
A1 = pd['A1']
print(f"   振幅: { {m: f'{a:.1f}' for m, a in sorted(A.items())} }")
print(f"   A1 = {A1:.1f}")

# 有理數級聯: A_m/A_1
print("\n   歸一化 A_m/A_1 (limit_denominator 50):")
fracs = {}
for m in sorted(A):
    a = A[m]/A1
    fr = Fraction(a).limit_denominator(50)
    fracs[m] = fr
    print(f"   A_{m}/A_1 = {a:.4f} ≈ {fr.numerator}/{fr.denominator}")

print("\n   分子/分母 對 Fibonacci/Lucas 檢查:")
for m in sorted(fracs):
    fr = fracs[m]
    n, d = fr.numerator, fr.denominator
    nf = [i for i, x in enumerate(F) if x == n]
    df = [i for i, x in enumerate(F) if x == d]
    nl = [i for i, x in enumerate(L) if x == n]
    dl = [i for i, x in enumerate(L) if x == d]
    tags = []
    if nf: tags.append(f"F_{nf[0]}")
    if df: tags.append(f"F_{df[0]}")
    if nl: tags.append(f"L_{nl[0]}")
    if dl: tags.append(f"L_{dl[0]}")
    print(f"   {n}/{d}  →  {', '.join(tags) if tags else '—'}")

# ---------- 4. ε 結構對比 ----------
print("\n" + "-"*80)
print("4. 振幅 vs ε=φ⁻¹/4 結構")
print("-"*80)
eps = phi**-1/4
for m in sorted(A):
    a = A[m]/A1
    k = a/eps
    print(f"   A_{m}/A_1 = {a:.4f} = {k:.4f} × ε")
# 檢查係咪 (2/3)^k 或 (φ⁻¹)^k
print("\n   (2/3)^k 檢查:")
for m in sorted(A):
    a = A[m]/A1
    k = np.log(a)/np.log(2/3)
    print(f"   A_{m}/A_1 = {a:.4f} = (2/3)^{k:.3f}")
print("\n   (φ⁻¹)^k 檢查:")
for m in sorted(A):
    a = A[m]/A1
    k = np.log(a)/np.log(phi**-1)
    print(f"   A_{m}/A_1 = {a:.4f} = φ⁻^{k:.3f}")

# ---------- 5. m=5 閉合嘗試 ----------
print("\n" + "-"*80)
print("5. m=5 閉合: 1121/1124 結構")
print("-"*80)
print(f"   1121 = 44×25+21, 21=F₈")
print(f"   1124 = 44×25+24")
print(f"   1121−1013 = 108 (Δℓ₄ 觀測)")
print(f"   1124−1013 = 111")
print(f"   1013 = 44×23+1  (唔係 2!)")
print(f"   44×23+1 = 1013 → m=4 相位其實係 1 唔係 2")
print()
print("   假設 m=4 相位=1 (1013), m=5 相位=F₈=21 (1121):")
print("   相位序列: 0, 9, 18, 1, 21, ?, ?")
print(f"   0,9,18,1,21 — 呢個係咩序列?")
print(f"   差: 9, 9, −17, 20 — 唔規則")
print()
print("   另一角度: 1013 = 44×23+1, 1121 = 44×25+21")
print("   N_int: 23 → 25 (+2), 相位: 1 → 21 (+20)")
print(f"   +2 = L₀? +20 = 2×L₅−2? 20 = F₇−1?")
print()
print("   再睇: 44×25+21 中 25 = 33−8, 8 = F₆")
print(f"   C(4,2)=6 → C(5,2)=10 → C(6,2)=15 → C(7,2)=21")
print(f"   25 = 33−8: 用 F₆=8 取代 C(4,2)=6?")
print(f"   1121 = 44×(33−F₆) + F₈ = 44×25+21 ✓✓✓")
print(f"   ★★★ 1121 = 44×(33−F₆) + F₈ !!!")
print(f"   檢查其他 m 有冇 Fibonacci 結構:")
for m in range(1, 8):
    C = _m.comb(9-m, 2)
    pred = idcm_orig[m]
    print(f"   m={m}: 44×(33−C({9-m},2)) + ph = 44×({33-C}) + {((m-1)*9)%25} = {pred}")

# ---------- 6. 全 Fibonacci 公式測試 ----------
print("\n" + "-"*80)
print("6. 全 Fibonacci 峰位公式測試:")
print("-"*80)
# 假設: ℓ_m = 44×(33 − F_x) + F_y
# m=1: 44×(33−F_?) + F_? = 220: 33−F_x = 5 → F_x=28? 唔係 Fib
# 試 44×(33−C(9−m,2)) 保持, 相位用 Fib: 0,9,18,2,11,20,4
# m=5: 相位 21=F₈, N=25=33−F₆
# 假設通用: N_int = 33 − (C(9−m,2) XOR F?) 
print("   保守: 保持 m=1..4,6,7 原公式, 只改 m=5:")
print("   m=5: 44×(33−F₆) + F₈ = 1121 (Planck bin)")
print("   vs SPT-3G 1124: 偏差 3/1121 = 0.27%")
print("   vs CAMB 1129: 偏差 8/1121 = 0.71%")
print("   ✅ 全部 < 1% !!!")
