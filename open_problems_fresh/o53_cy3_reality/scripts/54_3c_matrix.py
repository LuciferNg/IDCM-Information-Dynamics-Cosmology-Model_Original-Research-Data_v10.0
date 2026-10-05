#!/usr/bin/env python3
"""
O53 A1 深化: 3c 矩陣結構搜索
=================================
3c 矩陣 (代×電荷):
[[ 1  3 -2]
 [ 2 -2 -1]
 [ 0 -2  3]]

試:
  1. 行列式/跡
  2. 有冇排列令佢變 magic square
  3. 3c 同「三代 × 三電荷」嘅 su(3) 結構?
  4. 3c 值 = f(代, 電荷) 線性模型?
"""
import os, json, math
import numpy as np

print("=" * 70)
print("O53 A1: 3c 矩陣結構")
print("=" * 70)

M = np.array([[1, 3, -2], [2, -2, -1], [0, -2, 3]])
print(f"\n[1] 3c 矩陣:")
print(M)

# --- [1] 基本不變量 ---
det = np.linalg.det(M)
trace = np.trace(M)
print(f"\n[2] 不變量:")
print(f"    det = {det:.2f}")
print(f"    tr = {trace:.2f}")
print(f"    ΣΣ = {M.sum():.2f}")
print(f"    Σ 代² = {np.sum(M**2)}")

# 特徵值
ev = np.linalg.eigvals(M)
print(f"    本徵值 = {np.array2string(ev, precision=3)}")

# --- [2] 排列搜索 magic square ---
print("\n[3] Magic square 搜索 (行/列/對角和):")
row_sums = M.sum(axis=1)
col_sums = M.sum(axis=0)
diag1 = M[0,0]+M[1,1]+M[2,2]
diag2 = M[0,2]+M[1,1]+M[2,0]
print(f"    行和: {row_sums}")
print(f"    列和: {col_sums}")
print(f"    對角和: {diag1}, {diag2}")

# --- [3] 線性模型 3c = a·gen + b·Q + c? ---
print("\n[4] 線性模型 3c = a·g + b·q + c:")
gens = np.array([[1,1,1],[2,2,2],[3,3,3]])
qs = np.array([[2,-1,-2],[2,-1,-2],[2,-1,-2]])  # ×3 電荷
# solve
A = np.column_stack([gens.ravel(), qs.ravel(), np.ones(9)])
y = M.ravel()
coef, res, rank, sv = np.linalg.lstsq(A, y, rcond=None)
print(f"    3c = {coef[0]:+.3f}·g + {coef[1]:+.3f}·q + {coef[2]:+.3f}")
pred = A @ coef
err = np.abs(pred - y)
print(f"    max err = {err.max():.3f}, mean err = {err.mean():.3f}")

# --- [4] 3c 同 CKM/PMNS 角? ---
print("\n[5] 3c 同混合角?")
print(f"    3c 值域 [-2, +3] — 6 值 = 3! (permutations)")
print(f"    3 代 × 3 電荷 = 9 = 3²")

# --- [5] 3c 總和 = 2? ---
print("\n[6] Σ3c = 2:")
print(f"    Σ3c = 2 = 44−42? 2 = B−2?")
print(f"    Σ3c/9 = 2/9 = 0.222 ≈ Vus?")
print(f"    Σ3c = 2 = μ²? (O41: 差=μ²=2)")
print(f"    → Σ3c = 2 同 O41 嘅 μ² = 2 呼應!")

# --- [6] 3c 嘅 su(3) 結構 ---
print("\n[7] su(3) 結構:")
print(f"    su(3) 正根: 3 (α₁, α₂, α₁+α₂)")
print(f"    su(3) dim: 8")
print(f"    3c 值域 6 值 = su(3) 根數 - 3?")
print(f"    6 = C(4,2)? = 6 ✓ (again!)")
print(f"    3×3 矩陣 = su(3) 生成元空間 (8D) 嘅 subset")

# --- [7] 最重要: 3c 同 m 嘅直接關係 ---
print("\n[8] 3c vs log10(m):")
Ms = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
c3v = {'t': 1, 'b': 3, 'c': 2, 'tau': -2, 's': -2, 'mu': -1, 'd': -2, 'u': 0, 'e': 3}
for k in Ms:
    print(f"    {k:4s}: log10(m) = {math.log10(Ms[k]):+7.3f}  3c = {c3v[k]:+d}")

print("\n" + "=" * 70)
print("搜索完成")
print("=" * 70)
