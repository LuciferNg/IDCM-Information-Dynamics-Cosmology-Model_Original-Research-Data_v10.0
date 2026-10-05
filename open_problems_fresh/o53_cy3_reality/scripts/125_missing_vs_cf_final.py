#!/usr/bin/env python3
"""
O53 整合測試: 缺失 divisors [2,3,6,7] ↔ 3c_f 值
====================================================
缺失 divisors (0-based): [2, 3, 6, 7]
3c_f 值 (9 粒子): {0, ±1, ±2, 3}

有趣: 缺失 2,3,6,7 — 而 3c_f 有 2, 3, 2, 2, 1, 3...
6 = 2×3, 7 = ?

檢查: 有冇「4 個缺失」↔「4 個 c_f 值」對應?
"""
import os, json, math, sys
import numpy as np

print("=" * 70)
print("O53: 缺失 divisors ↔ 3c_f")
print("=" * 70)

missing = [2, 3, 6, 7]
cf3 = {'t': 1, 'b': 3, 'c': 2, 'tau': -2, 's': -2, 'mu': -1, 'd': -2, 'u': 0, 'e': 3}

print(f"[1] 缺失 divisors: {missing}")
print(f"[2] 3c_f 值: {sorted(set(cf3.values()))}")
print(f"  出現次數: {np.bincount([abs(v) for v in cf3.values()], minlength=4)}")

# 4 個缺失 ↔ 4 個 c_f?
# 3c_f 嘅絕對值: 0,1,1,2,2,2,2,3,3 → 9 個值
# 缺失 4 個: 2,3,6,7
# 6 = 2+3+1? 7 = 2+3+2?

print(f"\n[3] 數字關係:")
print(f"  缺失: 2, 3, 6, 7")
print(f"  2+3 = 5 = B+1")
print(f"  6+7 = 13 = F₆? (13 = F₇)")
print(f"  2+3+6+7 = 18 = det(3c_f)")
print(f"  2×3 = 6 (缺失入面!)")
print(f"  3c_f 嘅 Σ = 2 (總和)")
print(f"  缺失 Σ = 18 = det!")

# 18 = det(3c_f) = Σ(missing divisors)!
print(f"\n[4] 關鍵: Σ(missing) = 2+3+6+7 = 18 = |det(3c_f)|!")
print(f"  但呢個係巧合? 4 個數和 = 18 好常見")

# 檢查: 3c_f 矩陣 det = 18
M = np.array([[0,-2,3],[2,-2,-1],[1,3,-2]])
det = round(np.linalg.det(M))
print(f"  det(3c_f) = {det}")
print(f"  Σ(missing) = {sum(missing)}")
print(f"  相等? {det == sum(missing)}")

# 其他關係
print(f"\n[5] 更多關係:")
print(f"  3c_f 嘅 9 值: {list(cf3.values())}")
print(f"  Σ(3c) = {sum(cf3.values())}")
print(f"  缺失 Σ = {sum(missing)}")
print(f"  |Σ(3c)| + Σ(missing) = {abs(sum(cf3.values())) + sum(missing)} = 20")
print(f"  20 = B×F₅ = 4×5 ✓ (O13 n/p 機制)")
print(f"  Σ(3c)² = 36 = h11 (已撤銷 - 偽閉合)")
print(f"  Σ(missing)² = 4+9+36+49 = 98 = h12!!!")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)