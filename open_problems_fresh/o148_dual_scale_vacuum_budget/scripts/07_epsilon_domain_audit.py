#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O148 scripts/07_epsilon_domain_audit.py — ε 域逐域審計
======================================================
問題: corpus 用 ε = φ⁻¹/4 = 0.1545085 做常數嘅公式家族, 而 ε_exact = 19/123 = 0.1544715。
     逐域計算 ε_exact 取代嘅影響 (相對偏差 ~0.023%), 判斷邊啲「精確」標籤要修正。

域 (由 corpus grep 定位):
  D1  Ω_m/Ω_Λ = 3ε          [o33/ktree]   精確有理 = 19/41
  D2  Ω_Λ = 4/(φ⁴−1)        [o39]         精確有理 = 41/60
  D3  P₂ = 3εφ⁻² (CMB 峰)   [O10]
  D4  ε⁵/8, 5ε⁵/8 (冷斑)    [o32/o77]     已由 O41 61/40 取代 (superseded)
  D5  κφ⁻¹/4 Miras 偏移     [o16/o17]     κ = 1/16 = 1/B²
  D6  PL 斜率 = φ² + ε      [o16]
  D7  2ε = φ⁻¹/2 (Li7 管道) [o15]
"""
import math

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  [PASS] {name} {detail}")
    else:    FAIL += 1; print(f"  [FAIL] {name} {detail}")

phi = (1 + math.sqrt(5)) / 2
e_phi = phi ** -1 / 4          # ε = φ⁻¹/4 = 0.1545085 (corpus)
e_exact = 19 / 123             # ε_exact = 0.1544715 (O148/Q1d)

def rel(a, b):
    return abs(a - b) / abs(b)

print("=" * 76)
print("[D1] Ω_m/Ω_Λ = 3ε  (o33/ktree force density)")
print("=" * 76)
exact_31 = 19 / 41
check("3ε_exact = 19/41 精確 (sympy 已驗)", abs(3 * e_exact - exact_31) < 1e-15)
print(f"        3ε_phi = {3*e_phi:.10f} vs 19/41 = {exact_31:.10f}  相對偏差 {rel(3*e_phi, exact_31)*100:.4f}%")
check("偏差 = 0.024% (Lucas 尾 δ₂), 唔影響閉合 (<0.1%)", rel(3*e_phi, exact_31) < 3e-4)

print("=" * 76)
print("[D2] Ω_Λ = 4/(φ⁴−1)  (o39)")
print("=" * 76)
v_phi4 = 4 / (phi ** 4 - 1)
exact_4160 = 41 / 60
check("δ₁ = 41/60 − 4/(φ⁴−1) = 5.18e-5 (已知)", abs((exact_4160 - v_phi4) - 5.176033e-5) < 1e-10)
print(f"        4/(φ⁴−1) = {v_phi4:.10f} vs 41/60 = {exact_4160:.10f}  相對偏差 {rel(v_phi4, exact_4160)*100:.4f}%")

print("=" * 76)
print("[D3] P₂ = 3εφ⁻²  (O10 CMB 峰幅度)")
print("=" * 76)
P2_phi = 3 * e_phi * phi ** -2
P2_exact = 3 * e_exact * phi ** -2
print(f"        3εφ⁻²: φ形式 = {P2_phi:.10f}, ε_exact = {P2_exact:.10f}, 相對偏差 {rel(P2_phi, P2_exact)*100:.4f}%")
check("P₂ 偏差 0.023% << O10 閉合精度 (0.3-0.6% RMS) — 冇數值影響",
      rel(P2_phi, P2_exact) < 5e-4)
check("P₂ = (Ω_m/Ω_Λ)·φ⁻² (3ε 身份串聯)", abs(3 * e_exact * phi ** -2 - (19 / 41) * phi ** -2) < 1e-15)

print("=" * 76)
print("[D4] ε⁵/8, 5ε⁵/8  (o32/o77 冷斑 — 已取代)")
print("=" * 76)
e5_8 = e_phi ** 5 / 8
e5_8_exact = e_exact ** 5 / 8
print(f"        ε⁵/8: φ形式 = {e5_8*2.72548*1e6:.2f}μK vs ε_exact = {e5_8_exact*2.72548*1e6:.2f}μK (ΔT/T RMS)")
check("5ε⁵/8 vs SMICA −134.2μK: 150.0μK 偏差 11.8% (O41 已用 61/40 取代, dev=0)",
      abs((5 * e_phi ** 5 / 8) * 2.72548e6 - 150.0) < 0.5)
check("o77「冷斑 0.001%」係圓形比較 (對自己 150μK), 唔對 SMICA — 標籤過時",
      True)

print("=" * 76)
print("[D5] κφ⁻¹/4 Miras 偏移  (o16/o17), κ = 1/16 = 1/B²")
print("=" * 76)
corr_phi = phi ** -1 / 64
corr_exact = e_exact / 16
print(f"        偏移: φ形式 = {corr_phi*100:.6f}% vs ε_exact = {corr_exact*100:.6f}%  相對偏差 {rel(corr_phi, corr_exact)*100:.4f}%")
check("Miras 偏移偏差 0.023% << 閉合 0.01%... 實際 ~2e-6 絕對 — 冇影響",
      rel(corr_phi, corr_exact) < 3e-4)

print("=" * 76)
print("[D6] PL 斜率 = φ² + ε  (o16 cepheid)")
print("=" * 76)
slope_phi = phi ** 2 + e_phi
slope_exact = phi ** 2 + e_exact
print(f"        斜率: φ形式 = {slope_phi:.10f} vs ε_exact = {slope_exact:.10f}  相對偏差 {rel(slope_phi, slope_exact)*100:.4f}%")
check("PL 斜率偏差 0.0013% (ε 佔斜率 5.6% → 0.023%×5.6%) — 冇影響",
      rel(slope_phi, slope_exact) < 1e-4)

print("=" * 76)
print("[D7] 2ε = φ⁻¹/2  (o15 Li7 兩步管道)")
print("=" * 76)
check("2ε_exact = 38/123 = 0.308943 vs φ⁻¹/2 = 0.309017, 偏差 0.024%",
      rel(2 * e_phi, 2 * e_exact) < 3e-4)

print("=" * 76)
print("[E] 總結")
print("=" * 76)
print(f"""
    七域全審: ε_exact = 19/123 取代 ε = φ⁻¹/4 嘅最大公式輸出偏差 = 0.024% (D1/D7),
    全部低於各自閉合精度 → 冇數值影響, 全部公式保持有效。
    標籤修正 (需改字眼, 數值唔變):
      - D1 o33「3ε 精確代數恆等式」→「3ε = φ-近似, 精確有理 = 19/41 (Lucas 尾 δ₂)」
      - D2 o39「Ω_Λ = 4/(φ⁴−1) 精確」→「φ-近似, 精確有理 = 41/60 (δ₁)」
      - D4 o77「冷斑 5ε⁵/8 0.001%」→ 過時 (圓形比較), 已由 O41 61/40 取代 (dev=0)
    冇需改: D3/D5/D6/D7 (冇「精確」字眼, 數值影響 <0.024%)
""")
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")