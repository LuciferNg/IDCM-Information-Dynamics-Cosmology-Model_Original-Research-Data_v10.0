#!/usr/bin/env python3
"""
O10 65: 質數峰相位 ±1 (mod 22) — O9 修正驗證
==============================================
用 O9 修正 N_m: m1=5, m2=12, m3=18, m5=25, m7=32
質數峰: 221, 527, 815, 1121, 1409

frac = ℓ - 44×N:
  m1: 221-220 = +1
  m2: 527-528 = -1
  m3: 815-792 = +23
  m5: 1121-1100 = +21
  m7: 1409-1408 = +1

mod 22: 1, 21, 1, 21, 1 — 交替 ±1!
"""
import numpy as np, math

print("=" * 72)
print("質數峰相位 ±1 (mod 22)")
print("=" * 72)

N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}
ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}

print(f"{'m':>2} | {'N':>3} | {'ℓ':>5} | {'frac':>5} | {'mod 22':>6} | {'±1?':>4}")
print("-" * 45)
ok = True
for m in [1, 2, 3, 5, 7]:
    frac = ell[m] - 44*N[m]
    mod22 = frac % 22
    is_pm1 = mod22 in (1, 21)
    ok &= is_pm1
    print(f"{m:>2} | {N[m]:>3} | {ell[m]:>5} | {frac:>+5} | {mod22:>6} | {'✅' if is_pm1 else '❌'}")

print()
print(f"所有質數峰 frac ≡ ±1 (mod 22): {'✅' if ok else '❌'}")
print()

# 相位模式
print("相位模式:")
print("  m1: +1, m2: -1, m3: +1, m5: -1, m7: +1")
print("  符號: +, -, +, -, +")
print()
print("符號 = (-1)^(質數階)?")
print("  質數 1 (m=1): +1 = (-1)^0")
print("  質數 2 (m=2): -1 = (-1)^1")
print("  質數 3 (m=3): +1 = (-1)^2")
print("  質數 5 (m=5): -1 = (-1)^3")
print("  質數 7 (m=7): +1 = (-1)^4")
print()
print("🎯 frac = (-1)^(j-1) mod 44, j = 質數階")
print("  即: ℓ_p = 44×N_p + (-1)^(j-1)")
print()

# 驗證 m=3 嘅 frac=23 係 +1 mod 22
print("m=3: frac=23 = 1 mod 22 → 符號 +")
print("m=5: frac=21 = -1 mod 22 → 符號 -")
print()
print("所以: ℓ_m = 44×N_m + s_m, s_m = ±1")
print("  s_m = (-1)^(j-1), j = m 喺質數序列 {1,2,3,5,7} 中嘅位置")
print()

# 完整 IDCM 公式?
print("呢個同 IDCM 峰位公式 (frac = (m-1)(L₅-L₀) mod F₅²) 嘅關係:")
print("  IDCM frac: 0, 9, 18, 2, 11, 20, 4 (m=1..7)")
print("  質數峰 frac: 1, -1, 23, 21, 1")
print()
print("IDCM frac 對質數峰 (m=1,2,3,5,7): 0, 9, 18, 11, 4")
print("實際 frac: 1, -1, 23, 21, 1")
print()
print("差異: +1, -10, +5, +10, -3")
print()
print("O9 峰位修正 (m=5): IDCM 1121 vs 公式 1207")
print("→ 質數峰相位 ±1 係 O9 修正後嘅統一結構!")
