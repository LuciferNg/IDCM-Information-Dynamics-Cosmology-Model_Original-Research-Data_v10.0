#!/usr/bin/env python3
"""
O10 62: M/(M+1) 物理意義 + 質數峰機制
=======================================
M/(M+1) = 33/34: K_Tree 33 層 / 34 節點?

K_Tree: B=4, 深度 M=33 → 34 個 scale 層 (0..33)
M/(M+1) = 已佔用層/總層數?

質數峰出現機制: 點解只有質數位置有真峰?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
M = 33

print("=" * 72)
print("M/(M+1) 物理意義")
print("=" * 72)
print(f"M = {M} (K_Tree 層數), M+1 = 34 = F₉")
print(f"M/(M+1) = {M/(M+1):.6f}")
print()

# 其他候選
candidates = {
    "M/(M+1)": M/(M+1),
    "(M-1)/M": (M-1)/M,
    "1-1/(M+1)": 1-1/(M+1),
    "1-1/F₉": 1-1/34,
    "1-1/(M+F₁)": 1-1/34,
    "Σγ/(Σγ+1)": 90/91,
    "N/(N+1)": 44/45,
    "(N-1)/N": 43/44,
    "M/(M+2)": 33/35,
    "1-ε²/2.42": 1-eps**2/2.42,
}
target = 0.9702
print("候選對 0.9702:")
for name, val in candidates.items():
    dev = (val-target)/target*100
    if abs(dev) < 1:
        print(f"  {name} = {val:.6f} (偏差 {dev:+.4f}%)")

print()
print("→ M/(M+1) 最自然: K_Tree 33 層中已耦合 33/34")

# 質數峰機制
print()
print("=" * 72)
print("質數峰出現機制分析")
print("=" * 72)
print("真峰: m ∈ {1,2,3,5,7} (質數), 合數峰 4,6 唔存在")
print()

# 檢查質數同 K_Chain 模式嘅關係
print("質數 m 對應 K_Chain 模式 n?")
print("  峰位: ℓ_m = 44×N_m + frac")
N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}
for m in [1, 2, 3, 5, 7]:
    print(f"  m={m}: N_m = {N[m]}, 44-N = {44-N[m]}")
print()

# 質數峰 = 奇偶?
print("質數: 2 偶, 3,5,7 奇")
print("但 4, 6 係偶合數 — 質數特性先係關鍵")
print()

# 峰位差
print("峰位差 Δℓ:")
ells = [221, 527, 815, 1121, 1409]
diffs = [ells[i+1]-ells[i] for i in range(4)]
print(f"  Δℓ: {diffs}")
print(f"  306, 288, 306, 288 — 交替!")
print(f"  306 = 44×7-2 = 308-2? 288 = 44×6.545?")
print(f"  306 = 3×102 = 3×44×2.318?")
print(f"  288 = 44×6 + 24 = 288 ✓")
print(f"  306 = 44×7 - 2 = 306 ✓")
print()

# Δℓ 結構
print("Δℓ 對應 ΔN:")
dN = [12-5, 18-12, 25-18, 32-25]
print(f"  ΔN: {dN} = 7, 6, 7, 7")
print(f"  Δℓ = 44×ΔN + Δfrac")
print()

# 質數峰模式: m 係質數, ΔN 有 7,6,7,7
print("質數峰模式:")
print("  質數: 1, 2, 3, 5, 7")
print("  間隔: 1, 1, 2, 2")
print("  ΔN:   7, 6, 7, 7")
print()
print("間隔 1,1,2,2 對應 ΔN 7,6,7,7?")
print("  2→3 (隔1): ΔN=6")
print("  3→5 (隔2): ΔN=7")
print("  5→7 (隔2): ΔN=7")
print()

# 嘗試: ΔN = 8-m?
print("ΔN = 8-m? (完整 IDCM 結構)")
for i, m in enumerate([1, 2, 3, 5]):
    print(f"  m={m}→{ [1,2,3,5,7][i+1] }: ΔN = {dN[i]}, 8-m = {8-m}")

print()
print("質數峰嘅 ΔN 唔係 8-m (因為跳過合數)")
print("但質數對 (2,3) ΔN=6, (5,7) ΔN=7")
print()

# 檢查質數同 N_m 直接關係
print("N_m vs 質數:")
for m in [1, 2, 3, 5, 7]:
    p = m
    print(f"  m={p} (質數): N={N[m]}, N-p={N[m]-p}, N/p={N[m]/p:.3f}")
print()
print("N/p: 5, 6, 6, 5, 4.57")
print("N-4p: 1, 4, 6, 5, 4")
print()

# 關鍵: N_m = p_m + p_{m+1}? (之前試過)
primes = [2, 3, 5, 7, 11, 13]
print("質數對和:")
for i, m in enumerate([1, 2, 3, 5]):
    if i+1 < 5:
        s = primes[i] + primes[i+1]
        print(f"  p_{i+1}+p_{i+2} = {primes[i]}+{primes[i+1]} = {s} vs N_m = {N[m]}")
print()
print("5=2+3 ✓, 12=5+7 ✓, 18=7+11 ✓, 32=13+19 ✓")
print("N₅ = 25 = 11+14? 唔得... 或者 2+23 = 25 ✓")
