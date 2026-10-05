#!/usr/bin/env python3
"""
O53 A1 最後嘗試: c_f = n/3 嘅 3 因子來源
=============================================
h11 = 36 = 3×12 = 3 × (Nd−2B)/3
h12 = 98 = Σγ + 2B

問題: c_f ∈ {±1, ±2/3, ±1/3, 0} 嘅 1/3 結構係咪嚟自 36 = 3×12?

3c_f 矩陣:
  gen1 (u,d,e): [0,-2,3]
  gen2 (c,s,μ): [2,-2,-1]
  gen3 (t,b,τ): [1,3,-2]
  det = 18, ΣΣ = 2, Σ(3c)² = 36

新測試: 36 = 3×12 嘅 3 因子 → c_f = n/3?
"""
import os, json, math, sys
import numpy as np

print("=" * 70)
print("O53: c_f 3 因子來源")
print("=" * 70)

# 3c_f 矩陣
M = np.array([
    [0, -2, 3],
    [2, -2, -1],
    [1, 3, -2]
])
print(f"[1] 3c_f 矩陣:")
print(M)

# 分析
print(f"\n[2] 結構分析:")
print(f"  det = {np.linalg.det(M):.0f}")
print(f"  tr = {np.trace(M):.0f}")
print(f"  Σ(3c)² = {np.sum(M**2)} = 36 = h11 ✓")
print(f"  ΣΣ = {M.sum()}")

# 每行 (代) 分析
print(f"\n[3] 每代:")
for i, name in enumerate(['代1 (u,d,e)', '代2 (c,s,μ)', '代3 (t,b,τ)']):
    row = M[i]
    print(f"  {name}: {row}, 和={row.sum()}, 平方和={np.sum(row**2)}")

# 每列 (電荷) 分析
print(f"\n[4] 每電荷:")
for j, name in enumerate(['Q_up', 'Q_down', 'Q_lepton']):
    col = M[:, j]
    print(f"  {name}: {col}, 和={col.sum()}, 平方和={np.sum(col**2)}")

# 關鍵: 36 = 3×12 分解
# 3 因子 = 三代
# 12 因子 = block 大小
print(f"\n[5] 36 = 3×12:")
print(f"  3 = 三代 (t/b/c, τ/s/μ, d/u/e)")
print(f"  12 = (Nd−2B)/3 = (44−8)/3")
print(f"  3×12 = 36 = h11")
print(f"  12 維 = su(12) block")

# c_f 結構 = 每代 × 每電荷
# 3×3 矩陣: 行 = 代, 列 = 電荷
# 每 entry = c_f × 3

# 檢查: c_f 嘅 n/3 係咪 12 維結構?
# 12 = block 大小 → 每 block 12 個 divisors
# 3 個 block → 36 = h11
# 粒子 = 3 代 × 3 電荷 = 9
# 9 = 12 − 3? 或者 9 = 3²

print(f"\n[6] 粒子結構:")
print(f"  9 粒子 = 3 代 × 3 電荷")
print(f"  9 = 3² (三代平方)")
print(f"  12 − 9 = 3 (剩餘?)")
print(f"  36 = 4 × 9 = B × 3² (之前發現)")
print(f"  98 = 90 + 8 = Σγ + 2B")

# 3c_f 矩陣嘅行列式 18
print(f"\n[7] det = 18:")
print(f"  18 = 2×9 = 2×3²")
print(f"  18 = 36/2 = h11/2")
print(f"  18 = 90/5 = Σγ/5")
print(f"  18 = (Nd−2B)/2 = 36/2 ✓")

# 矩陣 M 嘅 SVD
U, s, Vt = np.linalg.svd(M)
print(f"\n[8] SVD:")
print(f"  singular values: {s}")
print(f"  s² = {s**2}")
print(f"  Σs² = {np.sum(s**2)} = tr(M·Mᵀ) = {np.sum(M**2)} ✓")

# 本徵值
ev = np.linalg.eigvals(M)
print(f"\n[9] 本徵值: {ev}")
print(f"  |λ|: {np.abs(ev)}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)