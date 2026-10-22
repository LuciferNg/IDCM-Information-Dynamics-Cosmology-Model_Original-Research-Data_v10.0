#!/usr/bin/env python3
"""
O10 22: 簡併對內部不對稱性 — 隱藏結構
======================================
發現: A_{2m}/A_{2m+1} = 0.87, 0.91, 0.96 (Planck)
      → 每對嘅偶峰 (2m) 矮過奇峰 (2m+1), 比率趨向 1

呢個比率有冇結構?
  0.866 (m=2), 0.913 (m=3), 1.010 (m=1)
  或者: 用理論修正後?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

# Planck @ O9 峰位 (A_pl from 21)
A_pl = {1: 1.0000, 2: 0.4434, 3: 0.4389, 4: 0.1856, 5: 0.2143, 6: 0.1303, 7: 0.1427}

print("簡併對內部比率 (Planck):")
ratios = {}
for m, (a, b) in {1: (2,3), 2: (4,5), 3: (6,7)}.items():
    r = A_pl[a]/A_pl[b]
    ratios[m] = r
    print(f"  A{a}/A{b} = {r:.4f}  (理論 1)")

print()
print("候選結構:")
# r₁ = 1.010, r₂ = 0.866, r₃ = 0.913
# 試: r_m = 1 - δ_m?
d = {1: 1-ratios[1], 2: 1-ratios[2], 3: 1-ratios[3]}
for m, v in d.items():
    print(f"  δ_{m} = 1 - r_{m} = {v:+.4f}")

print()
print("δ/ε:", {m: v/eps for m, v in d.items()})
print("δ/ε²:", {m: v/eps**2 for m, v in d.items()})

# 試: δ_m = ε·φ^(-a_m)?
print()
print("候選: δ_m = ε·φ^{-m}?")
for m in [1, 2, 3]:
    v = eps*phi**(-m)
    print(f"  m={m}: εφ⁻^{m} = {v:.4f} vs δ={d[m]:+.4f}")

print()
print("候選: δ_m ∝ (m-1)/m (harmonic)?")
for m in [1, 2, 3]:
    v = (m-1)/m
    print(f"  m={m}: (m-1)/m = {v:.4f} vs δ={d[m]:+.4f}")

# 另一個角度: 絕對高度唔係 P_m, 而係每峰獨立 A_m?
print()
print("=" * 72)
print("每峰獨立 A_m (唔係簡併對)")
print("=" * 72)
# A_m/A₁: 1, 0.4434, 0.4389, 0.1856, 0.2143, 0.1303, 0.1427
# 每峰 vs 理論?
# P_m 理論係對平均。每峰理論?
# 如果簡併完美: A_{2m} = A_{2m+1} = P_m
# 實際: A_{2m} < P_m < A_{2m+1}
P_th = {1: 3*eps, 2: 3*eps*phi**-2, 3: 3*eps*2*phi**-4}
print(f"{'峰':>2} | {'A_obs':>7} | {'P_m 理論':>8} | {'偏差':>8}")
for m in range(2, 8):
    pm = P_th[(m+1)//2]
    dev = (A_pl[m]-pm)/pm*100
    print(f"{m:>2} | {A_pl[m]:>7.4f} | {pm:>8.4f} | {dev:>+7.2f}%")

print()
print("注意: 每對嘅 2m (偶) 峰偏差負, 2m+1 (奇) 峰偏差正!")
print("→ 峰 m 嘅相位 (frac part) 決定高度偏移?")
# IDCM frac: m=4→9, m=5→18, m=6→2, m=7→11
fracs = {1: 0, 2: 9, 3: 18, 4: 2, 5: 11, 6: 20, 7: 4}
print("\nIDCM frac part:")
for m in range(2, 8):
    print(f"  m={m}: frac={fracs[m]}, A偏差={'+' if A_pl[m] > P_th[(m+1)//2] else '-'}")
