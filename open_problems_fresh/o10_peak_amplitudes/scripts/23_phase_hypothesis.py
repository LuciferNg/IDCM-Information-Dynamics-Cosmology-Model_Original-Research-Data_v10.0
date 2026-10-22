#!/usr/bin/env python3
"""
O10 23: 每峰獨立 A_m — 相位假設
================================
IDCM 峰位: ℓ_m = 44×N_m + frac_m
frac: m=1→0, 2→9, 3→18, 4→2, 5→11, 6→20, 7→4

假設: 峰高 A_m 由 N_m (整數部分) 主導, frac 微調?
或者: A_m 直接 = 3ε·F_m·φ^{-2(m-1)} 但每峰獨立讀?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

# Planck @ O9 峰位
A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 4: 0.1856, 5: 0.2143, 6: 0.1303, 7: 0.1427}
N = {1: 5, 2: 12, 3: 18, 4: 23, 5: 25, 6: 30, 7: 32}  # O9: m=5 用 25 (1121/44)
frac = {1: 0, 2: 9, 3: 18, 4: 2, 5: 11, 6: 20, 7: 4}

# 每峰對應嘅 P_m 理論 (簡併對平均)
P_th_map = {2: 3*eps, 3: 3*eps, 4: 3*eps*phi**-2, 5: 3*eps*phi**-2,
            6: 3*eps*2*phi**-4, 7: 3*eps*2*phi**-4}

print("每峰 vs 簡併對理論:")
for m in range(2, 8):
    th = P_th_map[m]
    dev = (A[m]-th)/th*100
    print(f"  m={m}: N={N[m]}, frac={frac[m]:2d}, A={A[m]:.4f}, 理論={th:.4f}, 偏差={dev:+.2f}%")

print()
print("偏差模式 (每對):")
for m, (a, b) in {1: (2,3), 2: (4,5), 3: (6,7)}.items():
    da = (A[a]-P_th_map[a])/P_th_map[a]*100
    db = (A[b]-P_th_map[b])/P_th_map[b]*100
    print(f"  對{m} ({a},{b}): 偏差 {da:+.2f}% / {db:+.2f}%  (平均 {(da+db)/2:+.2f}%)")

print()
print("=" * 72)
print("關鍵: 每對嘅偏差和 (pair sum) ≈ 0?")
print("=" * 72)
for m, (a, b) in {1: (2,3), 2: (4,5), 3: (6,7)}.items():
    da = (A[a]-P_th_map[a])/P_th_map[a]
    db = (A[b]-P_th_map[b])/P_th_map[b]
    print(f"  對{m}: δa+δb = {da+db:+.4f} (≈0 表示簡併對平均閉合)")

print()
print("但: m=2 對 (4,5) 嘅平均都 +12.9%!")
print("→ P₂ 用 O9 峰位 (1121) 反而更差?")
print("→ 檢查: 峰5 @ 1121 係咪真峰?")
print("  O9 三源: Planck 1121 / SPT 1124 / ACT 1098")
print("  → 峰 5 @ 1121 三實驗一致 (0.214/0.213/0.204)")
print("  → 呢個唔係散射, 係系統性高!")