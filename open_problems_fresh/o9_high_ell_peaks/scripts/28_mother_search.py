#!/usr/bin/env python3
"""
O9-C3: 母函數候選評估 — 系統化 Fib/Lucas 組合搜尋
=====================================================
目標: 搵到 A_m/A_1 或者相鄰比率嘅統一生成函數

已知信號:
- A2/A1 = (F₃/F₄)² = (2/3)²
- A6/A5 ≈ F₆/F₇ (1.1%)

候選母函數類型:
1. A_m/A_1 = (F_{a(m)}/F_{b(m)})²  — Fib 平方
2. A_m/A_1 = F_{k(m)}/L_{j(m)}     — Fib/Lucas 混合
3. A_{m+1}/A_m = F_{p(m)}/F_{q(m)} — 相鄰 Fib 比
4. 奇偶分離: 偶峰 (2/3)^k, 奇峰另一序列
5. 連分數生成: [a₀; a₁, a₂, ...] 遞歸
"""
import numpy as np
from fractions import Fraction
import itertools

print("="*80)
print("O9-C3: 母函數候選系統化搜尋")
print("="*80)

F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

# 觀測振幅 (Planck bin D_ℓ)
A_obs = {1: 5816.5, 2: 2579.2, 3: 2552.7, 4: 1079.5, 5: 1246.3, 6: 757.9, 7: 830.2}
A1 = A_obs[1]
norm = {m: A_obs[m]/A1 for m in range(1, 8)}
print("\n觀測歸一化振幅 A_m/A_1:")
for m in range(1, 8):
    print(f"   m={m}: {norm[m]:.4f}")

# ---------- 1. 每項 vs Fib/Lucas 比 ----------
print("\n" + "-"*80)
print("1. A_m/A_1 vs 所有 F_i/F_j 比 (i,j ≤ 14):")
print("-"*80)
for m in range(2, 8):
    target = norm[m]
    best = []
    for i in range(2, 14):
        for j in range(2, 14):
            r = F[i]/F[j]
            dev = abs(r - target)/target*100
            if dev < 3:
                best.append((dev, f"F_{i}/F_{j}={r:.4f}"))
            # 平方
            r2 = (F[i]/F[j])**2
            dev2 = abs(r2 - target)/target*100
            if dev2 < 3:
                best.append((dev2, f"(F_{i}/F_{j})²={r2:.4f}"))
    best.sort()
    print(f"   m={m} ({target:.4f}):")
    for dev, s in best[:4]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 2. 相鄰比率 vs Fib 比 ----------
print("\n" + "-"*80)
print("2. 相鄰比率 A_{m+1}/A_m vs Fib 比:")
print("-"*80)
for m in range(1, 7):
    target = A_obs[m+1]/A_obs[m]
    best = []
    for i in range(2, 14):
        for j in range(2, 14):
            r = F[i]/F[j]
            dev = abs(r - target)/target*100
            if dev < 3:
                best.append((dev, f"F_{i}/F_{j}={r:.4f}"))
            r2 = (F[i]/F[j])**2
            dev2 = abs(r2 - target)/target*100
            if dev2 < 3:
                best.append((dev2, f"(F_{i}/F_{j})²={r2:.4f}"))
    best.sort()
    print(f"   A{m+1}/A{m} ({target:.4f}):")
    for dev, s in best[:4]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 3. Lucas 比 ----------
print("\n" + "-"*80)
print("3. A_m/A_1 vs Lucas 比 L_i/L_j:")
print("-"*80)
for m in range(2, 8):
    target = norm[m]
    best = []
    for i in range(1, 12):
        for j in range(1, 12):
            if L[j] == 0: continue
            r = L[i]/L[j]
            dev = abs(r - target)/target*100
            if dev < 3:
                best.append((dev, f"L_{i}/L_{j}={r:.4f}"))
            r2 = (L[i]/L[j])**2
            dev2 = abs(r2 - target)/target*100
            if dev2 < 3:
                best.append((dev2, f"(L_{i}/L_{j})²={r2:.4f}"))
    best.sort()
    print(f"   m={m} ({target:.4f}):")
    for dev, s in best[:3]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 4. 混合 Fib/Lucas ----------
print("\n" + "-"*80)
print("4. A_m/A_1 vs F_i/L_j 混合:")
print("-"*80)
for m in range(2, 8):
    target = norm[m]
    best = []
    for i in range(2, 14):
        for j in range(1, 12):
            if L[j] == 0: continue
            r = F[i]/L[j]
            dev = abs(r - target)/target*100
            if dev < 3:
                best.append((dev, f"F_{i}/L_{j}={r:.4f}"))
    best.sort()
    print(f"   m={m} ({target:.4f}):")
    for dev, s in best[:3]:
        print(f"      {s} dev={dev:.2f}%")

# ---------- 5. 指數結構 ----------
print("\n" + "-"*80)
print("5. (2/3)^k 指數 vs 整數/半整數:")
print("-"*80)
for m in range(1, 8):
    k = np.log(norm[m])/np.log(2/3)
    k2 = round(2*k)/2
    print(f"   m={m}: k={k:.3f} → 半整數 {k2} (Δ={abs(k-k2):.3f})")

# ---------- 6. 奇偶分離 ----------
print("\n" + "-"*80)
print("6. 奇偶峰分離:")
print("-"*80)
odd = {m: norm[m] for m in [1, 3, 5, 7]}
even = {m: norm[m] for m in [2, 4, 6]}
print(f"   奇峰: {[f'{v:.4f}' for v in odd.values()]}")
print(f"   偶峰: {[f'{v:.4f}' for v in even.values()]}")
print(f"   奇峰比 (A3/A1, A5/A3, A7/A5): {norm[3]/norm[1]:.3f}, {norm[5]/norm[3]:.3f}, {norm[7]/norm[5]:.3f}")
print(f"   偶峰比 (A4/A2, A6/A4): {norm[4]/norm[2]:.3f}, {norm[6]/norm[4]:.3f}")
